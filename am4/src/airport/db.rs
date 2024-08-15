/*!
Implements an in-memory, indexed airport database.

An airport has unique identifiers (such as [Iata], [Icao], [Name] etc.)
and we wish to query it in O(1) given the primary key.

## Database building
Given &[[Airport]], build hashmaps that point [SearchKey]s to the array index.

## Searching
1. Given user input (&[str]), e.g. `iata:hkg`, `hkg`
2. Parse into a [QueryKey], e.g. IATA("hkg"), All("hkg")
3. Convert it into the primary key.
    - in the case of [QueryKey::All] (general search), attempt all [SearchKey]s.
4. Dereference the associated array index to get the airport.
*/

use crate::airport::{Airport, AirportError, Iata, Icao, Id, Name};
use crate::utils::ParseError;
use crate::utils::{queue_suggestions, Suggestion, MAX_SUGGESTIONS};
use jaro_winkler::jaro_winkler;
use rkyv::{self, Deserialize};
use std::collections::BinaryHeap;
use std::collections::HashMap;
use std::str::FromStr;
use thiserror::Error;

pub const AIRPORT_COUNT: usize = 3907;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum SearchKey {
    Id(Id),
    Iata(Iata),
    Icao(Icao),
    Name(Name),
}

impl From<Id> for SearchKey {
    fn from(id: Id) -> Self {
        SearchKey::Id(id)
    }
}

impl From<Iata> for SearchKey {
    fn from(iata: Iata) -> Self {
        SearchKey::Iata(Iata(iata.0.to_uppercase()))
    }
}

impl From<Icao> for SearchKey {
    fn from(icao: Icao) -> Self {
        SearchKey::Icao(Icao(icao.0.to_uppercase()))
    }
}

impl From<Name> for SearchKey {
    fn from(name: Name) -> Self {
        SearchKey::Name(Name(name.0.to_uppercase()))
    }
}

#[derive(Debug, Clone)]
pub enum QueryKey {
    All(String),
    Id(Id),
    Iata(Iata),
    Icao(Icao),
    Name(Name),
}

impl FromStr for QueryKey {
    type Err = AirportSearchError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let s = s.trim();

        if s.is_empty() {
            return Err(AirportSearchError::EmptyQuery);
        }

        let key = match s.to_uppercase().split_once(':') {
            None => QueryKey::All(s.to_string()),
            Some((k, v)) => match k {
                "IATA" => QueryKey::Iata(Iata(v.to_string())),
                "ICAO" => QueryKey::Icao(Icao(v.to_string())),
                "NAME" => QueryKey::Name(Name(v.to_string())),
                "ID" => QueryKey::Id(Id::from_str(v)?),
                v => return Err(AirportSearchError::InvalidColumnSpecifier(v.to_string())),
            },
        };

        Ok(key)
    }
}

impl From<QueryKey> for Result<SearchKey, AirportSearchError> {
    fn from(key: QueryKey) -> Self {
        match &key {
            QueryKey::All(s) => {
                if let Ok(v) = Id::from_str(s) {
                    Ok(SearchKey::from(v))
                } else if let Ok(v) = Iata::from_str(s) {
                    Ok(SearchKey::from(v))
                } else if let Ok(v) = Icao::from_str(s) {
                    Ok(SearchKey::from(v))
                } else if let Ok(v) = Name::from_str(s) {
                    Ok(SearchKey::from(v))
                } else {
                    // all parsers failed, we can be sure it does not exist in the database
                    Err(AirportSearchError::AirportNotFound(key.clone()))
                }
            }
            QueryKey::Id(id) => Ok(SearchKey::from(id.clone())),
            QueryKey::Iata(iata) => Ok(SearchKey::from(iata.clone())),
            QueryKey::Icao(icao) => Ok(SearchKey::from(icao.clone())),
            QueryKey::Name(name) => Ok(SearchKey::from(name.clone())),
        }
    }
}

/// An immutable collection of indexed airports, stored entirely in-memory.
///
/// This must be created from a rkyv archive of a [`Vec<Airport>`] via [Self::from_bytes].
#[derive(Debug)]
pub struct Airports {
    data: Vec<Airport>,
    index: HashMap<SearchKey, usize>,
}

impl Airports {
    pub fn from_bytes(buffer: &[u8]) -> Result<Self, ParseError> {
        let archived = rkyv::check_archived_root::<Vec<Airport>>(buffer)
            .map_err(|e| ParseError::ArchiveError(e.to_string()))?;

        let data: Vec<Airport> = archived
            .deserialize(&mut rkyv::Infallible)
            .map_err(|e| ParseError::DeserialiseError(e.to_string()))?;

        let mut index = HashMap::<SearchKey, usize>::new();

        for (i, ap) in data.iter().enumerate() {
            index.entry(SearchKey::from(ap.idx.clone())).or_insert(i);
            index.entry(SearchKey::from(ap.iata.clone())).or_insert(i);
            index.entry(SearchKey::from(ap.icao.clone())).or_insert(i);
            index.entry(SearchKey::from(ap.name.clone())).or_insert(i);
        }

        Ok(Self { data, index })
    }

    /// Search for an airport
    pub fn search(&self, s: &str) -> Result<&Airport, AirportSearchError> {
        let qkey = QueryKey::from_str(s)?;
        let key = Result::<SearchKey, AirportSearchError>::from(qkey.clone())?;

        self.index
            .get(&key)
            .map(|i| &self.data[*i])
            .ok_or(AirportSearchError::AirportNotFound(qkey))
    }

    pub fn suggest(&self, s: &str) -> Result<Vec<Suggestion<&Airport>>, AirportSearchError> {
        let ctx = QueryKey::from_str(s)?;
        self.suggest_by_ctx(&ctx)
    }

    pub fn suggest_by_ctx(
        &self,
        qkey: &QueryKey,
    ) -> Result<Vec<Suggestion<&Airport>>, AirportSearchError> {
        // TODO: this is a hack to get the uppercase version of the parsed query
        let key = Result::<SearchKey, AirportSearchError>::from(qkey.clone())?;
        let su = match key {
            SearchKey::Iata(v) => v.0.clone(),
            SearchKey::Icao(v) => v.0.clone(),
            SearchKey::Name(v) => v.0.clone(),
            SearchKey::Id(v) => v.0.to_string(),
        };

        let mut heap = BinaryHeap::with_capacity(MAX_SUGGESTIONS);

        for (key, &i) in &self.index {
            // TODO: restrict to only search by shortname if ctx.key is shortname
            let s = match key {
                SearchKey::Iata(v) => &v.0,
                SearchKey::Icao(v) => &v.0,
                SearchKey::Name(v) => &v.0,
                _ => continue, // ignore searching by id
            };
            let similarity = jaro_winkler(s, &su);
            queue_suggestions(&mut heap, &self.data[i], similarity);
        }

        Ok(heap.into_sorted_vec())
    }

    pub fn data(&self) -> &Vec<Airport> {
        &self.data
    }

    pub fn index(&self) -> &HashMap<SearchKey, usize> {
        &self.index
    }
}

#[derive(Debug, Error)]
pub enum AirportSearchError {
    #[error("Empty query")]
    EmptyQuery,
    #[error("Invalid column specifier: `{0}`. Did you mean: `iata`, `icao`, `name` or `id`?")]
    InvalidColumnSpecifier(String),
    #[error("Query `{0:?}` returned no results.")]
    AirportNotFound(QueryKey),
    #[error(transparent)]
    Airport(#[from] AirportError),
}
