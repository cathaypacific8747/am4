use serde::Deserialize;
use std::fmt;
use std::fs::File;
use std::num::ParseIntError;
use std::str::FromStr;
use std::string::String;

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct Name(String);

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct FullName(String);

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct Iata(String);

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

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct Icao(String);

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

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct Id(u16);

impl FromStr for Id {
    type Err = Error;

    fn from_str(id: &str) -> Result<Self, Self::Err> {
        id.parse::<u16>().map(Self).map_err(Error::InvalidID)
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct Airport {
    id: Id,
    name: Name,
    fullname: FullName,
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
enum Query {
    ALL(String),
    IATA(Iata),
    ICAO(Icao),
    NAME(Name),
    FULLNAME(FullName),
    ID(Id),
}

impl Query {
    fn from_str(s: &str) -> Result<Self, Error> {
        match s.split_once(":") {
            None => Ok(Self::ALL(s.to_string())),
            Some((k, v)) => match k.to_lowercase().as_str() {
                "iata" => Iata::from_str(v).map(Self::IATA),
                "icao" => Icao::from_str(v).map(Self::ICAO),
                "name" => Ok(Self::NAME(Name(v.to_string()))),
                "fullname" => Ok(Self::FULLNAME(FullName(v.to_string()))),
                "id" => Id::from_str(v).map(Self::ID),
                _ => Err(Error::InvalidQueryType),
            },
        }
    }
}

#[derive(Debug, Clone)]
pub struct Airports {
    airports: Vec<Airport>,
}

impl Airports {
    pub fn from_csv(file_path: &str) -> Result<Self, csv::Error> {
        let file = File::open(file_path)?;
        let mut rdr = csv::Reader::from_reader(file);
        let mut airports = Vec::with_capacity(3907);

        for result in rdr.deserialize() {
            let airport: Airport = result?;
            airports.push(airport);
        }

        Ok(Self { airports })
    }

    pub fn search(&self, s: &str) -> Option<&Airport> {
        let mut it = self.airports.iter();
        let query = Query::from_str(s).unwrap();
        match query {
            Query::ALL(s) => self.search_all(&s),
            Query::IATA(iata) => it.find(|ap| ap.iata == iata),
            Query::ICAO(icao) => it.find(|ap| ap.icao == icao),
            Query::NAME(name) => it.find(|ap| ap.name == name),
            Query::FULLNAME(fullname) => it.find(|ap| ap.fullname == fullname),
            Query::ID(id) => it.find(|ap| ap.id == id),
        }
    }

    fn search_all(&self, s: &str) -> Option<&Airport> {
        let mut it = self.airports.iter();
        // first, attempt to infer the column type by try-parsing the input
        //     i.e. check IATA.len() == 3, ICAO.len() == 4, ID is u16able
        // if parsing fails or no match, search by name or fullname
        let infer_search_result = if let Ok(id) = Id::from_str(s) {
            it.find(|ap| ap.id == id)
        } else if let Ok(iata) = Iata::from_str(s) {
            it.find(|ap| ap.iata == iata)
        } else if let Ok(icao) = Icao::from_str(s) {
            it.find(|ap| ap.icao == icao)
        } else {
            None
        };
        infer_search_result.or_else(|| it.find(|ap| ap.name.0 == s || ap.fullname.0 == s))
    }
}

#[derive(Debug)]
pub enum Error {
    InvalidIATA,
    InvalidICAO,
    InvalidID(ParseIntError),
    InvalidQueryType,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::InvalidIATA => write!(f, "Invalid IATA: must be three characters"),
            Error::InvalidICAO => write!(f, "Invalid ICAO: must be four characters"),
            Error::InvalidID(e) => write!(f, "Invalid Airport ID: {}", e),
            Error::InvalidQueryType => write!(f, "Invalid query type"),
        }
    }
}
