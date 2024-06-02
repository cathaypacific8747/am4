use crate::aircraft::custom::{CustomAircraft, Modification};
use crate::aircraft::{Aircraft, AircraftError, EnginePriority, Id, Name, ShortName};
use crate::utils::ParseError;
use crate::utils::{queue_suggestions, Suggestion, MAX_SUGGESTIONS};
use jaro_winkler::jaro_winkler;
use rkyv::{self, Deserialize};
use std::collections::BinaryHeap;
use std::collections::HashMap;
use std::convert::Into;
use std::fs::File;
use std::io::Read;
use std::str::FromStr;

use thiserror::Error;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum SearchKey {
    Id(Id),
    ShortName(ShortName),
    Name(Name),
}

impl From<Id> for SearchKey {
    fn from(id: Id) -> Self {
        SearchKey::Id(id)
    }
}

impl From<ShortName> for SearchKey {
    fn from(sn: ShortName) -> Self {
        SearchKey::ShortName(ShortName(sn.0.to_uppercase()))
    }
}

impl From<Name> for SearchKey {
    fn from(name: Name) -> Self {
        SearchKey::Name(Name(name.0.to_uppercase()))
    }
}

#[derive(Debug)]
pub enum QueryKey {
    All(String),
    Id(Id),
    ShortName(ShortName),
    Name(Name),
}

#[derive(Debug)]
pub struct QueryCtx {
    pub key: QueryKey,
    pub modifiers: Modification,
}

impl FromStr for QueryCtx {
    type Err = AircraftSearchError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let (s, mods) = match s.trim().split_once('[') {
            None => (s, Modification::default()),
            Some((s, mods_str)) => {
                if let Some(end_idx) = mods_str.find(']') {
                    (s, Modification::from_str(&mods_str[..end_idx])?)
                } else {
                    return Err(AircraftSearchError::MissingClosingBracket);
                }
            }
        };

        let key = match s.to_uppercase().split_once(':') {
            None => QueryKey::All(s.to_string()),
            Some((k, v)) => match k {
                "SHORTNAME" => QueryKey::ShortName(ShortName(v.to_string())),
                "NAME" => QueryKey::Name(Name(v.to_string())),
                "ID" => QueryKey::Id(Id::from_str(v)?),
                _ => return Err(AircraftSearchError::InvalidQueryType),
            },
        };

        Ok(QueryCtx {
            key,
            modifiers: mods,
        })
    }
}

impl From<&QueryCtx> for Option<SearchKey> {
    fn from(val: &QueryCtx) -> Self {
        match &val.key {
            QueryKey::All(s) => {
                if let Ok(v) = Id::from_str(s) {
                    Some(SearchKey::from(v))
                } else if let Ok(v) = ShortName::from_str(s) {
                    Some(SearchKey::from(v))
                } else if let Ok(v) = Name::from_str(s) {
                    Some(SearchKey::from(v))
                } else {
                    None
                }
            }
            QueryKey::Id(id) => Some(SearchKey::from(id.clone())),
            QueryKey::ShortName(sn) => Some(SearchKey::from(sn.clone())),
            QueryKey::Name(name) => Some(SearchKey::from(name.clone())),
        }
    }
}

pub type AircraftVariants = HashMap<EnginePriority, usize>;

#[derive(Debug)]
pub struct Aircrafts {
    data: Vec<Aircraft>,
    index: HashMap<SearchKey, AircraftVariants>,
}

impl Aircrafts {
    pub fn from(file_path: &str) -> Result<Aircrafts, ParseError> {
        let mut file = File::open(file_path)?;
        let mut buffer = Vec::<u8>::new();
        file.read_to_end(&mut buffer)?;

        let archived = rkyv::check_archived_root::<Vec<Aircraft>>(&buffer)
            .map_err(|e| ParseError::ArchiveError(e.to_string()))?;

        let data: Vec<Aircraft> = archived
            .deserialize(&mut rkyv::Infallible)
            .map_err(|e| ParseError::DeserialiseError(e.to_string()))?;

        let mut index = HashMap::<SearchKey, AircraftVariants>::new();

        for (i, ac) in data.iter().enumerate() {
            index
                .entry(SearchKey::from(ac.id.clone()))
                .or_default()
                .insert(ac.priority.clone(), i);

            index
                .entry(SearchKey::from(ac.shortname.clone()))
                .or_default()
                .insert(ac.priority.clone(), i);

            index
                .entry(SearchKey::from(ac.name.clone()))
                .or_default()
                .insert(ac.priority.clone(), i);
        }

        Ok(Self { data, index })
    }

    /// Search for an aircraft, defaulting to the engine that gives the fastest speed, (priority == 0, fastest)
    pub fn search(&self, s: &str) -> Result<CustomAircraft, AircraftSearchError> {
        let ctx = QueryCtx::from_str(s)?;
        let engines = self.search_by_key(&ctx)?;

        if let Some(i) = engines.get(&ctx.modifiers.engine) {
            Ok(CustomAircraft::from_aircraft_and_modifiers(
                self.data[*i].to_owned(),
                ctx.modifiers,
            ))
        } else {
            Err(AircraftSearchError::EngineNotFound)
        }
    }

    /// Search all engine variants for a given aircraft
    pub fn search_engines(&self, s: &str) -> Result<&AircraftVariants, AircraftSearchError> {
        let ctx = QueryCtx::from_str(s)?;
        self.search_by_key(&ctx)
    }

    fn search_by_key(&self, ctx: &QueryCtx) -> Result<&AircraftVariants, AircraftSearchError> {
        let key: Option<SearchKey> = ctx.into();
        let key = key.ok_or(AircraftSearchError::InvalidQueryType)?;

        self.index
            .get(&key)
            .ok_or(AircraftSearchError::AircraftNotFound)
    }

    pub fn suggest(&self, s: &str) -> Result<Vec<Suggestion<&Aircraft>>, AircraftSearchError> {
        let ctx = QueryCtx::from_str(s)?;

        // TODO: this is a hack to get the uppercase version of the parsed query
        let key: Option<SearchKey> = (&ctx).into();
        let key = key.ok_or(AircraftSearchError::InvalidQueryType)?;
        let su = match key {
            SearchKey::ShortName(v) => v.0,
            SearchKey::Name(v) => v.0,
            SearchKey::Id(v) => v.0.to_string(),
        };

        let mut heap = BinaryHeap::with_capacity(MAX_SUGGESTIONS);

        for (key, variants) in &self.index {
            // only search first engine variant
            // TODO: restrict to only search by shortname if ctx.key is shortname
            if let Some(i) = variants.values().next() {
                let s = match key {
                    SearchKey::ShortName(v) => &v.0,
                    SearchKey::Name(v) => &v.0,
                    _ => continue, // ignore searching by id
                };
                let similarity = jaro_winkler(s, &su);
                queue_suggestions(&mut heap, &self.data[*i], similarity);
            }
        }

        Ok(heap.into_sorted_vec())
    }

    // getter only - no modification after building allowed
    pub fn data(&self) -> &Vec<Aircraft> {
        &self.data
    }

    pub fn index(&self) -> &HashMap<SearchKey, AircraftVariants> {
        &self.index
    }
}

#[derive(Debug, Error)]
pub enum AircraftSearchError {
    #[error("Invalid query type")]
    InvalidQueryType,
    #[error("Aircraft not found")]
    AircraftNotFound,
    #[error("Engine does not exist for this aircraft")]
    EngineNotFound,
    #[error("Found opening `[` but no closing `]`.")]
    MissingClosingBracket,
    #[error(transparent)]
    Aircraft(#[from] AircraftError),
}
