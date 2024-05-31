use crate::aircraft::custom::{CustomAircraft, Modifiers};
use crate::aircraft::{Aircraft, AircraftError, Id, Name, Priority, ShortName};
use crate::utils::{Preprocess, Suggestion};
use jaro_winkler::jaro_winkler;
use std::collections::BinaryHeap;
use std::collections::HashMap;
use std::fs::File;
use std::str::FromStr;

use thiserror::Error;

const COUNT: usize = 331;
const MAX_SUGGESTIONS: usize = 5;

impl Preprocess for Id {
    fn preprocess(&self) -> Self {
        Self(self.0)
    }
}

impl Preprocess for ShortName {
    fn preprocess(&self) -> Self {
        Self(self.0.to_uppercase())
    }
}

impl Preprocess for Name {
    fn preprocess(&self) -> Self {
        Self(self.0.to_uppercase())
    }
}

#[derive(Debug)]
pub enum QueryKey {
    ALL(String),
    ID(Id),
    SHORTNAME(ShortName),
    NAME(Name),
}

#[derive(Debug)]
pub struct QueryCtx {
    pub key: QueryKey,
    pub modifiers: Modifiers,
}

impl FromStr for QueryCtx {
    type Err = AircraftSearchError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let mut mods = Modifiers::default();

        let s = if let Some(idx) = s.find('[') {
            if let Some(end_idx) = s.find(']') {
                for c in s[idx + 1..end_idx].to_lowercase().chars() {
                    match c {
                        's' => mods.speed_mod = true,
                        'f' => mods.fuel_mod = true,
                        'c' => mods.co2_mod = true,
                        'x' => mods.fourx_mod = true,
                        'e' => mods.easy_boost = true,
                        ' ' | ',' => {}
                        p => match Priority::from_str(&p.to_string()) {
                            Ok(pri) => mods.priority = pri,
                            Err(e) => return Err(e.into()),
                        },
                    }
                }
                s[..idx].trim()
            } else {
                return Err(AircraftSearchError::InvalidModifier(
                    "Found opening `[` but no closing `]`.".to_string(),
                ));
            }
        } else {
            s.trim()
        };

        match s.to_uppercase().split_once(':') {
            None => Ok(QueryCtx {
                key: QueryKey::ALL(s.to_string()),
                modifiers: mods,
            }),
            Some((k, v)) => match k {
                "SHORTNAME" => Ok(QueryCtx {
                    key: QueryKey::SHORTNAME(ShortName(v.to_string())),
                    modifiers: mods,
                }),
                "NAME" => Ok(QueryCtx {
                    key: QueryKey::NAME(Name(v.to_string())),
                    modifiers: mods,
                }),
                "ID" => Ok(Id::from_str(v).map(|id| QueryCtx {
                    key: QueryKey::ID(id),
                    modifiers: mods,
                })?),
                _ => Err(AircraftSearchError::InvalidQueryType),
            },
        }
    }
}

pub type AircraftVariants<'a> = HashMap<Priority, &'a Aircraft>;

#[derive(Debug)]
pub struct Aircrafts {
    data: Vec<Aircraft>,
}

impl Aircrafts {
    pub fn from_csv(file_path: &str) -> Result<Self, csv::Error> {
        let file = File::open(file_path)?;
        let mut rdr = csv::Reader::from_reader(file);

        let mut aircrafts = Self {
            data: Vec::with_capacity(COUNT),
        };

        for result in rdr.deserialize() {
            let ac: Aircraft = result?;
            aircrafts.data.push(ac);
        }

        Ok(aircrafts)
    }

    pub fn indexed<'a>(&'a self) -> AircraftsIndex<'a> {
        AircraftsIndex::new(&self.data)
    }
}

/// A generic index that can be used to index any type by a key
/// that is extracted from the value.
#[derive(Debug)]
pub struct Index<'a, K: Eq + std::hash::Hash + Preprocess> {
    index: HashMap<K, AircraftVariants<'a>>,
}

impl<'a, K: Eq + std::hash::Hash + Preprocess> Index<'a, K> {
    /// Create a new index.
    ///
    /// The `data` parameter is a slice of the data to index.
    /// The `key_fn` parameter is a closure that takes a reference to an
    /// element of the data and returns the key to use for that element.
    fn new(data: &'a [Aircraft], key_fn: fn(&Aircraft) -> K) -> Self {
        let mut index = HashMap::new();
        for aircraft in data {
            let key = key_fn(aircraft);
            index
                .entry(key.preprocess())
                .or_insert_with(HashMap::new)
                .insert(aircraft.priority.clone(), aircraft);
        }
        Self { index }
    }

    /// Get the variants for a given key.
    fn get(&self, key: &K) -> Option<&AircraftVariants<'a>> {
        self.index.get(&key.preprocess())
    }
}

#[derive(Debug)]
pub struct AircraftsIndex<'a> {
    pub by_id: Index<'a, Id>,
    pub by_shortname: Index<'a, ShortName>,
    pub by_name: Index<'a, Name>,
    _data: &'a [Aircraft], // keep data so index references remain valid
}

impl<'a> AircraftsIndex<'a> {
    pub fn new(data: &'a [Aircraft]) -> Self {
        Self {
            by_id: Index::new(data, |ac| ac.id.clone()),
            by_shortname: Index::new(data, |ac| ac.shortname.clone()),
            by_name: Index::new(data, |ac| ac.name.clone()),
            _data: data,
        }
    }

    /// Search for an aircraft by any key.
    pub fn search(&'a self, s: &str) -> Result<CustomAircraft, AircraftSearchError> {
        let ctx = QueryCtx::from_str(s)?;

        let ac = self.search_variants_(&ctx)?;
        ac.get(&ctx.modifiers.priority)
            .map(|ac| {
                CustomAircraft::from_aircraft_and_modifiers(ac.to_owned().to_owned(), ctx.modifiers)
            })
            .ok_or(AircraftSearchError::AircraftPriorityNotFound)
    }

    /// Search for an aircraft by any key, and return all variants.
    pub fn search_variants(
        &'a self,
        s: &str,
    ) -> Result<&HashMap<Priority, &'a Aircraft>, AircraftSearchError> {
        let ctx = QueryCtx::from_str(s)?;
        self.search_variants_(&ctx)
    }

    // TODO: this is really dumb.
    fn search_variants_(
        &'a self,
        ctx: &QueryCtx,
    ) -> Result<&HashMap<Priority, &'a Aircraft>, AircraftSearchError> {
        match &ctx.key {
            QueryKey::ALL(s) => {
                if let Ok(id) = Id::from_str(s) {
                    self.by_id.get(&id)
                } else if let Ok(sn) = ShortName::from_str(s) {
                    self.by_shortname.get(&sn)
                } else if let Ok(name) = Name::from_str(s) {
                    self.by_name.get(&name)
                } else {
                    None
                }
            }
            QueryKey::ID(id) => self.by_id.get(id),
            QueryKey::SHORTNAME(sn) => self.by_shortname.get(sn),
            QueryKey::NAME(name) => self.by_name.get(name),
        }
        .ok_or(AircraftSearchError::AircraftNotFound)
    }
}

fn queue_suggestions<'a>(
    heap: &mut BinaryHeap<Suggestion<&'a Aircraft>>,
    aircraft: &'a Aircraft,
    similarity: f64,
) {
    if heap.len() < MAX_SUGGESTIONS {
        heap.push(Suggestion::<&'a Aircraft> {
            item: aircraft,
            similarity,
        });
    } else if similarity > heap.peek().unwrap().similarity {
        heap.pop();
        heap.push(Suggestion::<&'a Aircraft> {
            item: aircraft,
            similarity,
        });
    }
}

impl<'a> AircraftsIndex<'a> {
    pub fn suggest(&'a self, s: &str) -> Vec<Suggestion<&'a Aircraft>> {
        let su = s.to_uppercase();

        let mut heap = BinaryHeap::with_capacity(MAX_SUGGESTIONS);

        for ac_variants in self.by_shortname.index.values() {
            if let Some(aircraft) = ac_variants.values().next() {
                queue_suggestions(
                    &mut heap,
                    aircraft,
                    jaro_winkler(&aircraft.shortname.0, &su),
                );
            }
        }

        for ac_variants in self.by_name.index.values() {
            if let Some(aircraft) = ac_variants.values().next() {
                queue_suggestions(&mut heap, aircraft, jaro_winkler(&aircraft.name.0, &su));
            }
        }

        heap.into_sorted_vec()
    }
}

#[derive(Debug, Error)]
pub enum AircraftSearchError {
    #[error("Invalid query type")]
    InvalidQueryType,
    #[error("Aircraft not found")]
    AircraftNotFound,
    #[error("Aircraft priority not found")]
    AircraftPriorityNotFound,
    #[error("Invalid modifier: {0}")]
    InvalidModifier(String),
    #[error(transparent)]
    Aircraft(#[from] AircraftError),
}
