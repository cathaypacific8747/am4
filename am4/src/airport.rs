use jaro_winkler::jaro_winkler;
use serde::Deserialize;
use std::collections::{BinaryHeap, HashMap};
use std::fs::File;
use std::num::ParseIntError;
use std::rc::Rc;
use std::str::FromStr;
use std::string::String;

use crate::utils::Suggestion;
use thiserror::Error;

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
    pub id: Id,
    pub name: Name,
    pub fullname: String,
    pub country: String,
    pub continent: String,
    pub iata: Iata,
    pub icao: Icao,
    pub lat: f64,
    pub lng: f64,
    pub rwy: u16,
    pub market: u8,
    pub hub_cost: u32,
    pub rwy_codes: String,
}

#[derive(Debug)]
enum QueryKey {
    All(String),
    Iata(Iata),
    Icao(Icao),
    Name(Name),
    Id(Id),
}

impl FromStr for QueryKey {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().split_once(':') {
            None => Ok(Self::All(s.to_string())),
            Some((k, v)) => match k {
                "IATA" => Iata::from_str(v).map(Self::Iata),
                "ICAO" => Icao::from_str(v).map(Self::Icao),
                "NAME" => Ok(Self::Name(Name(v.to_string()))),
                "ID" => Id::from_str(v).map(Self::Id),
                _ => Err(Error::InvalidQueryType),
            },
        }
    }
}

#[derive(Debug, Clone)]
pub struct Airports {
    pub by_iata: HashMap<Iata, Rc<Airport>>,
    pub by_icao: HashMap<Icao, Rc<Airport>>,
    pub by_id: HashMap<Id, Rc<Airport>>,
    pub by_name: HashMap<Name, Rc<Airport>>,
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
            QueryKey::All(s) => {
                // first, attempt to infer the column type by try-parsing the input
                //     i.e. check IATA.len() == 3, ICAO.len() == 4, ID is u16-able
                // if parsing fails or no match, search by name
                if let Ok(id) = Id::from_str(&s) {
                    self.by_id.get(&id)
                } else if let Ok(iata) = Iata::from_str(&s) {
                    self.by_iata.get(&iata)
                } else if let Ok(icao) = Icao::from_str(&s) {
                    self.by_icao.get(&icao)
                } else {
                    self.by_name.get(&Name(s.to_string()))
                }
            }
            QueryKey::Iata(iata) => self.by_iata.get(&iata),
            QueryKey::Icao(icao) => self.by_icao.get(&icao),
            QueryKey::Name(name) => self.by_name.get(&name),
            QueryKey::Id(id) => self.by_id.get(&id),
        };
        result.ok_or(Error::NotFound)
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
    } else if similarity > heap.peek().unwrap().similarity {
        heap.pop();
        heap.push(Suggestion::<Rc<Airport>> {
            item: Rc::clone(airport),
            similarity,
        });
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

#[derive(Debug, Error)]
pub enum Error {
    #[error("Invalid IATA: must be three characters")]
    InvalidIATA,
    #[error("Invalid ICAO: must be four characters")]
    InvalidICAO,
    #[error("Invalid Airport ID: {0}")]
    InvalidID(#[from] ParseIntError),
    #[error("Invalid query type")]
    InvalidQueryType,
    #[error("Airport not found")]
    NotFound,
}

#[cfg(test)]
mod tests {
    use crate::airport::{Airports, Error, Iata, Icao, Id};
    use std::{num::ParseIntError, sync::Once};

    const AIRPORTS_CSV: &str = "data/airports.csv";

    static mut AIRPORTS: Option<Airports> = None;
    static INIT: Once = Once::new();

    fn setup_airports() -> &'static Airports {
        INIT.call_once(|| {
            let airports = Airports::from_csv(AIRPORTS_CSV).expect("Failed to load airports data");

            unsafe {
                AIRPORTS = Some(airports);
            }
        });

        unsafe { AIRPORTS.as_ref().unwrap() }
    }

    #[test]
    fn test_airport_search() -> Result<(), Error> {
        let airports = setup_airports();

        let test_cases = vec![
            ("id:3500", "HKG"),
            ("iata:Hkg", "HKG"),
            ("icao:vhhh", "HKG"),
            ("name:hong kong", "HKG"),
            // ("hong kong", "HKG"),
            // ("fullname:hong kong, hong kong", "HKG"),
            // ("hong kong, hong kong", "HKG"),
        ];

        for (input, expected_iata) in test_cases {
            let airport = airports.search(input)?;
            assert_eq!(airport.iata.0, *expected_iata);
        }

        Ok(())
    }

    #[test]
    fn test_airport_fail_and_suggest() -> Result<(), Error> {
        let airports = setup_airports();

        // let test_cases = vec!["VHHX  ", "iata:hkgA", "icao:VHHx", "name:hng kong"];
        let test_cases = vec!["VHHX  "];

        for input in test_cases {
            match airports.search(input) {
                Ok(_) => panic!("Expected search to fail for input: {}", input),
                Err(_) => {
                    let suggestions = airports.suggest(input);
                    assert_eq!(suggestions[0].item.iata.0, "HKG");
                }
            }
        }

        Ok(())
    }

    #[test]
    fn test_airport_stoi_overflow() -> Result<(), Error> {
        let airports = setup_airports();

        if let Err(e) = airports.search("65590") {
            assert!(matches!(e, Error::NotFound));
        } else {
            panic!("Expected search to fail for input: 65590");
        }

        if let Err(e) = airports.search("id:65590") {
            assert!(matches!(e, Error::InvalidID(ParseIntError { .. })));
        } else {
            panic!("Expected search to fail for input: id:65590");
        }

        Ok(())
    }

    #[test]
    fn test_airport_from_str() {
        let iata = "Hkg";
        let result = iata.parse::<Iata>().unwrap();
        assert_eq!(result.0, iata.to_uppercase());

        let icao = "vhhh";
        let result = icao.parse::<Icao>().unwrap();
        assert_eq!(result.0, icao.to_uppercase());

        let id = "3500";
        let result = id.parse::<Id>().unwrap();
        assert_eq!(result.0, 3500);
    }
}
