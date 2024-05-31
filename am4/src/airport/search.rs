use crate::airport::{Airport, AirportError, Iata, Icao, Id, Name};
use crate::utils::{queue_suggestions, Suggestion, MAX_SUGGESTIONS};
use jaro_winkler::jaro_winkler;
use std::collections::BinaryHeap;
use std::collections::HashMap;
use std::convert::Into;
use std::fs::File;
use std::str::FromStr;

use thiserror::Error;

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

#[derive(Debug)]
pub enum QueryKey {
    All(String),
    Id(Id),
    Iata(Iata),
    Icao(Icao),
    Name(Name),
}

#[derive(Debug)]
pub struct QueryCtx {
    pub key: QueryKey,
}

impl FromStr for QueryCtx {
    type Err = AirportSearchError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let s = s.trim();

        let key = match s.to_uppercase().split_once(':') {
            None => QueryKey::All(s.to_string()),
            Some((k, v)) => match k {
                "IATA" => QueryKey::Iata(Iata(v.to_string())),
                "ICAO" => QueryKey::Icao(Icao(v.to_string())),
                "NAME" => QueryKey::Name(Name(v.to_string())),
                "ID" => QueryKey::Id(Id::from_str(v)?),
                _ => return Err(AirportSearchError::InvalidQueryType),
            },
        };

        Ok(QueryCtx { key })
    }
}

impl Into<Option<SearchKey>> for QueryCtx {
    fn into(self) -> Option<SearchKey> {
        match &self.key {
            QueryKey::All(s) => {
                if let Ok(v) = Id::from_str(s) {
                    Some(SearchKey::from(v))
                } else if let Ok(v) = Iata::from_str(s) {
                    Some(SearchKey::from(v))
                } else if let Ok(v) = Icao::from_str(s) {
                    Some(SearchKey::from(v))
                } else if let Ok(v) = Name::from_str(s) {
                    Some(SearchKey::from(v))
                } else {
                    None
                }
            }
            QueryKey::Id(id) => Some(SearchKey::from(id.clone())),
            QueryKey::Iata(iata) => Some(SearchKey::from(iata.clone())),
            QueryKey::Icao(icao) => Some(SearchKey::from(icao.clone())),
            QueryKey::Name(name) => Some(SearchKey::from(name.clone())),
        }
    }
}

#[derive(Debug)]
pub struct Airports {
    pub data: Vec<Airport>,
}

impl Airports {
    pub fn from_csv(file_path: &str) -> Result<Self, csv::Error> {
        let file = File::open(file_path)?;
        let mut rdr = csv::Reader::from_reader(file);

        let mut airports = Self { data: Vec::new() };

        for result in rdr.deserialize() {
            let ap: Airport = result?;
            airports.data.push(ap);
        }

        Ok(airports)
    }

    pub fn indexed<'a>(&'a self) -> AirportsIndex<'a> {
        AirportsIndex::new(&self.data)
    }
}

#[derive(Debug)]
pub struct AirportsIndex<'a> {
    index: HashMap<SearchKey, &'a Airport>,
    _data: &'a [Airport],
}

impl<'a> AirportsIndex<'a> {
    pub fn new(data: &'a [Airport]) -> Self {
        let mut index: HashMap<SearchKey, &'a Airport> = HashMap::new();

        for airport in data {
            index.insert(SearchKey::from(airport.id.clone()), airport);
            index.insert(SearchKey::from(airport.iata.clone()), airport);
            index.insert(SearchKey::from(airport.icao.clone()), airport);
            index.insert(SearchKey::from(airport.name.clone()), airport);
        }

        Self { index, _data: data }
    }

    /// Search for an airport
    pub fn search(&'a self, s: &str) -> Result<&'a Airport, AirportSearchError> {
        let ctx = QueryCtx::from_str(s)?;
        let key: Option<SearchKey> = ctx.into();
        let key = key.ok_or(AirportSearchError::InvalidQueryType)?;

        self.index
            .get(&key)
            .ok_or(AirportSearchError::AirportNotFound)
            .copied()
    }

    pub fn suggest(&'a self, s: &str) -> Result<Vec<Suggestion<&'a Airport>>, AirportSearchError> {
        let ctx = QueryCtx::from_str(s)?;

        // TODO: this is a hack to get the uppercase version of the parsed query
        let key: Option<SearchKey> = ctx.into();
        let key = key.ok_or(AirportSearchError::InvalidQueryType)?;
        let su = match key {
            SearchKey::Iata(v) => v.0.clone(),
            SearchKey::Icao(v) => v.0.clone(),
            SearchKey::Name(v) => v.0.clone(),
            SearchKey::Id(v) => v.0.to_string(),
        };

        let mut heap = BinaryHeap::with_capacity(MAX_SUGGESTIONS);

        for (key, airport) in &self.index {
            // TODO: restrict to only search by shortname if ctx.key is shortname
            let s = match key {
                SearchKey::Iata(v) => &v.0,
                SearchKey::Icao(v) => &v.0,
                SearchKey::Name(v) => &v.0,
                _ => continue, // ignore searching by id
            };
            let similarity = jaro_winkler(s, &su);
            queue_suggestions(&mut heap, *airport, similarity);
        }

        Ok(heap.into_sorted_vec())
    }
}

#[derive(Debug, Error)]
pub enum AirportSearchError {
    #[error("Invalid query type")]
    InvalidQueryType,
    #[error("Airport not found")]
    AirportNotFound,
    #[error(transparent)]
    Airport(#[from] AirportError),
}
