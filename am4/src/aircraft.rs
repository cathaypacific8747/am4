use serde::Deserialize;
use std::collections::HashMap;
use std::fmt;
use std::fs::File;
use std::rc::Rc;
use std::str::FromStr;

// use crate::user::User;
use crate::utils::Suggestion;
use jaro_winkler::jaro_winkler;
use std::collections::BinaryHeap;

const COUNT: usize = 282;
const MAX_SUGGESTIONS: usize = 5;

#[derive(Debug, Clone, Copy, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum AircraftType {
    Pax,
    Cargo,
    Vip,
}

impl FromStr for AircraftType {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "pax" => Ok(Self::Pax),
            "cargo" => Ok(Self::Cargo),
            "vip" => Ok(Self::Vip),
            _ => Err(Error::InvalidAircraftType),
        }
    }
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct Priority(u8);

impl FromStr for Priority {
    type Err = Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        s.parse::<u8>()
            .map(Self)
            .map_err(Error::InvalidEnginePriority)
    }
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct Aircraft {
    pub id: u16,
    pub shortname: String,
    pub manufacturer: String,
    pub name: String,
    #[serde(rename = "type")]
    pub ac_type: AircraftType,
    pub priority: Priority,
    pub eid: u16,
    pub ename: String,
    pub speed: f32,
    pub fuel: f32,
    pub co2: f32,
    pub cost: u32,
    pub capacity: u32,
    pub rwy: u16,
    pub check_cost: u32,
    pub range: u16,
    pub ceil: u16,
    pub maint: u16,
    pub pilots: u8,
    pub crew: u8,
    pub engineers: u8,
    pub technicians: u8,
    pub img: String,
    pub wingspan: u8,
    pub length: u8,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Modifiers {
    pub speed_mod: bool,
    pub fuel_mod: bool,
    pub co2_mod: bool,
    pub fourx_mod: bool,
    pub easy_boost: bool,
    pub priority: Priority,
}

impl Default for Modifiers {
    fn default() -> Self {
        Modifiers {
            speed_mod: false,
            fuel_mod: false,
            co2_mod: false,
            fourx_mod: false,
            easy_boost: false,
            priority: Priority(0),
        }
    }
}

#[derive(Debug)]
pub struct CustomAircraft {
    pub aircraft: Rc<Aircraft>,
    pub modifiers: Modifiers,
}

impl CustomAircraft {
    pub fn new(aircraft: Rc<Aircraft>) -> Self {
        Self {
            aircraft,
            modifiers: Modifiers::default(),
        }
    }

    pub fn with_modifiers(&self, modifiers: Modifiers) -> Self {
        let mut ac = self.get_new_aircraft(&modifiers.priority); // deep copy
        if !self.modifiers.speed_mod && modifiers.speed_mod {
            ac.speed *= 1.1;
            ac.cost = (ac.cost as f32 * 1.07).ceil() as u32;
        }
        if !self.modifiers.fuel_mod && modifiers.fuel_mod {
            ac.fuel *= 0.9;
            ac.cost = (ac.cost as f32 * 1.10).ceil() as u32;
        }
        if !self.modifiers.co2_mod && modifiers.co2_mod {
            ac.co2 *= 0.9;
            ac.cost = (ac.cost as f32 * 1.05).ceil() as u32;
        }
        if !self.modifiers.fourx_mod && modifiers.fourx_mod {
            ac.speed *= 4.0;
        }
        if !self.modifiers.easy_boost && modifiers.easy_boost {
            ac.speed *= 1.5;
        }
        Self {
            aircraft: ac.into(),
            modifiers,
        }
    }

    fn get_new_aircraft(&self, priority: &Priority) -> Aircraft {
        if self.aircraft.priority == *priority {
            (*self.aircraft).clone()
        } else {
            unimplemented!("updating engine type not yet implemented");
        }
    }
}

#[derive(Debug)]
pub enum QueryKey {
    ALL(String),
    ID(u16),
    SHORTNAME(String),
    NAME(String),
}

#[derive(Debug)]
pub struct QueryCtx {
    pub key: QueryKey,
    pub modifiers: Modifiers,
}

impl QueryKey {
    fn from_str(s: &str) -> Result<QueryCtx, Error> {
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
                            Err(e) => return Err(e),
                        },
                    }
                }
                s[..idx].trim()
            } else {
                return Err(Error::InvalidModifier(
                    "Found opening `[` but no closing `]`.".to_string(),
                ));
            }
        } else {
            s.trim()
        };

        match s.to_uppercase().split_once(":") {
            None => Ok(QueryCtx {
                key: QueryKey::ALL(s.to_string()),
                modifiers: mods,
            }),
            Some((k, v)) => match k {
                "SHORTNAME" => Ok(QueryCtx {
                    key: QueryKey::SHORTNAME(v.to_string()),
                    modifiers: mods,
                }),
                "NAME" => Ok(QueryCtx {
                    key: QueryKey::NAME(v.to_string()),
                    modifiers: mods,
                }),
                "ID" => u16::from_str(v)
                    .map_err(Error::InvalidID)
                    .map(|id| QueryCtx {
                        key: QueryKey::ID(id),
                        modifiers: mods,
                    }),
                _ => Err(Error::InvalidQueryType),
            },
        }
    }
}

// TODO: hashmap<column name, hashmap<engine priority, Aircraft>>
#[derive(Debug, Clone)]
pub struct Aircrafts {
    by_id: HashMap<u16, Rc<Aircraft>>,
    by_shortname: HashMap<String, Rc<Aircraft>>,
    by_name: HashMap<String, Rc<Aircraft>>,
}

// TODO: implement IntoIterator returning by_id
impl Aircrafts {
    pub fn from_csv(file_path: &str) -> Result<Self, csv::Error> {
        let file = File::open(file_path)?;
        let mut rdr = csv::Reader::from_reader(file);
        let mut aircrafts = Self {
            by_id: HashMap::with_capacity(COUNT),
            by_shortname: HashMap::with_capacity(COUNT),
            by_name: HashMap::with_capacity(COUNT),
        };

        for result in rdr.deserialize() {
            let aircraft: Aircraft = result?;
            aircrafts.add_aircraft(aircraft);
        }

        Ok(aircrafts)
    }

    fn add_aircraft(&mut self, aircraft: Aircraft) {
        let ac = Rc::new(aircraft);

        self.by_id.insert(ac.id, Rc::clone(&ac));
        self.by_shortname
            .insert(ac.shortname.to_uppercase(), Rc::clone(&ac));
        self.by_name.insert(ac.name.to_lowercase(), Rc::clone(&ac));
    }

    pub fn search(&self, s: &str) -> Result<CustomAircraft, Error> {
        let ctx = QueryKey::from_str(s)?;
        let result = match ctx.key {
            QueryKey::ALL(s) => self.search_all(&s),
            QueryKey::ID(id) => self.by_id.get(&id),
            QueryKey::SHORTNAME(sn) => self.by_shortname.get(&sn.to_uppercase()),
            QueryKey::NAME(name) => self.by_name.get(&name.to_lowercase()),
        };
        result
            .map(|ac| CustomAircraft::new(Rc::clone(ac)).with_modifiers(ctx.modifiers))
            .ok_or(Error::NotFound)
    }

    fn search_all(&self, s: &str) -> Option<&Rc<Aircraft>> {
        if let Ok(id) = u16::from_str(s) {
            self.by_id.get(&id)
        } else if let Some(ac) = self.by_shortname.get(&s.to_uppercase()) {
            Some(ac)
        } else {
            self.by_name.get(&s.to_lowercase())
        }
    }
}

fn queue_suggestions(
    heap: &mut BinaryHeap<Suggestion<Rc<Aircraft>>>,
    aircraft: &Rc<Aircraft>,
    similarity: f64,
) {
    if heap.len() < MAX_SUGGESTIONS {
        heap.push(Suggestion::<Rc<Aircraft>> {
            item: Rc::clone(aircraft),
            similarity,
        });
    } else {
        if similarity > heap.peek().unwrap().similarity {
            heap.pop();
            heap.push(Suggestion::<Rc<Aircraft>> {
                item: Rc::clone(aircraft),
                similarity,
            });
        }
    }
}

impl Aircrafts {
    pub fn suggest(&self, s: &str) -> Vec<Suggestion<Rc<Aircraft>>> {
        let su = s.to_uppercase();

        let mut heap = BinaryHeap::with_capacity(MAX_SUGGESTIONS);

        for (k, aircraft) in self.by_shortname.iter() {
            queue_suggestions(&mut heap, aircraft, jaro_winkler(k, &su));
        }
        for (k, aircraft) in self.by_name.iter() {
            queue_suggestions(&mut heap, aircraft, jaro_winkler(k, &su));
        }
        heap.into_sorted_vec()
    }
}

#[derive(Debug)]
pub enum Error {
    InvalidID(std::num::ParseIntError),
    InvalidQueryType,
    NotFound,
    InvalidAircraftType,
    InvalidEnginePriority(std::num::ParseIntError),
    InvalidModifier(String),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::InvalidID(e) => write!(f, "Invalid aircraft ID: {}", e),
            Error::InvalidQueryType => write!(f, "Invalid query type"),
            Error::NotFound => write!(f, "Aircraft not found"),
            Error::InvalidAircraftType => write!(f, "Invalid aircraft type"),
            Error::InvalidEnginePriority(e) => write!(f, "Invalid engine priority: {}", e),
            Error::InvalidModifier(e) => write!(f, "Invalid modifier: {}", e),
        }
    }
}
