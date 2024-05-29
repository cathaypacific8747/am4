use jaro_winkler::jaro_winkler;
use serde::Deserialize;
use std::collections::{BinaryHeap, HashMap};
use std::fmt;
use std::fs::File;
use std::num::ParseIntError;
use std::rc::Rc;
use std::str::FromStr;
use std::string::String;

use super::utils::Suggestion;

const COUNT: usize = 3907;
const MAX_SUGGESTIONS: usize = 5;

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, Hash)]
pub struct Name(String);

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, Hash)]
pub struct Iata(String);

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, Hash)]
pub struct Icao(String);

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, Hash)]
pub struct Id(u16);

impl FromStr for Iata {
    type Err = Error;

    fn from_str(iata: &str) -> Result<Self, Self::Err> {
        if iata.len() == 3 {
            Ok(Self(iata.to_uppercase()))
        } else {
            Err(Error::InvalidIATA)
        }
    }
}

impl FromStr for Icao {
    type Err = Error;

    fn from_str(icao: &str) -> Result<Self, Self::Err> {
        if icao.len() == 4 {
            Ok(Self(icao.to_uppercase()))
        } else {
            Err(Error::InvalidICAO)
        }
    }
}

impl FromStr for Id {
    type Err = Error;

    fn from_str(id: &str) -> Result<Self, Self::Err> {
        id.parse::<u16>().map(Self).map_err(Error::InvalidID)
    }
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct Airport {
    id: Id,
    name: Name,
    fullname: String,
    country: String,
    continent: String,
    iata: Iata,
    icao: Icao,
    lat: f64,
    lng: f64,
    rwy: u16,
    market: u8,
    hub_cost: u32,
    rwy_codes: String,
}

#[derive(Debug)]
enum QueryKey {
    ALL(String),
    IATA(Iata),
    ICAO(Icao),
    NAME(Name),
    ID(Id),
}

impl QueryKey {
    fn from_str(s: &str) -> Result<Self, Error> {
        match s.to_uppercase().split_once(":") {
            None => Ok(Self::ALL(s.to_string())),
            Some((k, v)) => match k {
                "IATA" => Iata::from_str(v).map(Self::IATA),
                "ICAO" => Icao::from_str(v).map(Self::ICAO),
                "NAME" => Ok(Self::NAME(Name(v.to_string()))),
                "ID" => Id::from_str(v).map(Self::ID),
                _ => Err(Error::InvalidQueryType),
            },
        }
    }
}

#[derive(Debug, Clone)]
pub struct Airports {
    by_iata: HashMap<Iata, Rc<Airport>>,
    by_icao: HashMap<Icao, Rc<Airport>>,
    by_id: HashMap<Id, Rc<Airport>>,
    by_name: HashMap<Name, Rc<Airport>>,
}

impl Airports {
    pub fn from_csv(file_path: &str) -> Result<Self, csv::Error> {
        let file = File::open(file_path)?;
        let mut rdr = csv::Reader::from_reader(file);
        let mut airports = Self {
            by_iata: HashMap::with_capacity(COUNT),
            by_icao: HashMap::with_capacity(COUNT),
            by_id: HashMap::with_capacity(COUNT),
            by_name: HashMap::with_capacity(COUNT),
        };

        for result in rdr.deserialize() {
            let airport: Airport = result?;
            airports.add_airport(airport);
        }

        Ok(airports)
    }

    fn add_airport(&mut self, airport: Airport) {
        let ap = Rc::new(airport);

        self.by_id.insert(ap.id.clone(), Rc::clone(&ap));
        self.by_iata
            .insert(Iata(ap.iata.0.to_uppercase()), Rc::clone(&ap));
        self.by_icao
            .insert(Icao(ap.icao.0.to_uppercase()), Rc::clone(&ap));
        self.by_name
            .insert(Name(ap.name.0.to_uppercase()), Rc::clone(&ap));
    }

    pub fn search(&self, s: &str) -> Result<&Rc<Airport>, Error> {
        let query = QueryKey::from_str(s)?;
        let result = match query {
            QueryKey::ALL(s) => self.search_all(&s),
            QueryKey::IATA(iata) => self.by_iata.get(&iata),
            QueryKey::ICAO(icao) => self.by_icao.get(&icao),
            QueryKey::NAME(name) => self.by_name.get(&name),
            QueryKey::ID(id) => self.by_id.get(&id),
        };
        result.ok_or(Error::NotFound)
    }

    fn search_all(&self, s: &str) -> Option<&Rc<Airport>> {
        // first, attempt to infer the column type by try-parsing the input
        //     i.e. check IATA.len() == 3, ICAO.len() == 4, ID is u16-able
        // if parsing fails or no match, search by name
        if let Ok(id) = Id::from_str(s) {
            self.by_id.get(&id)
        } else if let Ok(iata) = Iata::from_str(s) {
            self.by_iata.get(&iata)
        } else if let Ok(icao) = Icao::from_str(s) {
            self.by_icao.get(&icao)
        } else {
            self.by_name.get(&Name(s.to_string()))
        }
    }
}

fn queue_suggestions(
    heap: &mut BinaryHeap<Suggestion<Rc<Airport>>>,
    airport: &Rc<Airport>,
    similarity: f64,
) {
    if heap.len() < MAX_SUGGESTIONS {
        heap.push(Suggestion::<Rc<Airport>> {
            item: Rc::clone(airport),
            similarity,
        });
    } else {
        if similarity > heap.peek().unwrap().similarity {
            heap.pop();
            heap.push(Suggestion::<Rc<Airport>> {
                item: Rc::clone(airport),
                similarity,
            });
        }
    }
}

impl Airports {
    pub fn suggest(&self, s: &str) -> Vec<Suggestion<Rc<Airport>>> {
        let su = s.to_uppercase();

        let mut heap = BinaryHeap::with_capacity(MAX_SUGGESTIONS);

        for (k, airport) in self.by_iata.iter() {
            queue_suggestions(&mut heap, airport, jaro_winkler(&k.0, &su));
        }
        for (k, airport) in self.by_icao.iter() {
            queue_suggestions(&mut heap, airport, jaro_winkler(&k.0, &su));
        }
        for (k, airport) in self.by_name.iter() {
            queue_suggestions(&mut heap, airport, jaro_winkler(&k.0, &su));
        }
        heap.into_sorted_vec()
    }
}

#[derive(Debug)]
pub enum Error {
    InvalidIATA,
    InvalidICAO,
    InvalidID(ParseIntError),
    InvalidQueryType,
    NotFound,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::InvalidIATA => write!(f, "Invalid IATA: must be three characters"),
            Error::InvalidICAO => write!(f, "Invalid ICAO: must be four characters"),
            Error::InvalidID(e) => write!(f, "Invalid Airport ID: {}", e),
            Error::InvalidQueryType => write!(f, "Invalid query type"),
            Error::NotFound => write!(f, "Airport not found"),
        }
    }
}
