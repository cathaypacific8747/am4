use serde::Deserialize;
use std::collections::HashMap;
use std::fs::File;
use std::rc::Rc;
use std::str::FromStr;

use crate::utils::Suggestion;
use jaro_winkler::jaro_winkler;
use std::collections::BinaryHeap;
use thiserror::Error;

const COUNT: usize = 331;
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
        match s.to_uppercase().as_str() {
            "PAX" => Ok(Self::Pax),
            "CARGO" => Ok(Self::Cargo),
            "VIP" => Ok(Self::Vip),
            _ => Err(Error::InvalidAircraftType),
        }
    }
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, Hash)]
pub struct Id(u16);

impl FromStr for Id {
    type Err = Error;

    fn from_str(id: &str) -> Result<Self, Self::Err> {
        id.parse::<u16>().map(Self).map_err(Error::InvalidID)
    }
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, Hash)]
pub struct ShortName(String);

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, Hash)]
pub struct Name(String);

#[derive(Debug, Clone, Deserialize, PartialEq, Eq, Hash)]
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
    pub id: Id,
    pub shortname: ShortName,
    pub manufacturer: String,
    pub name: Name,
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
    type Err = Error;

    fn from_str(s: &str) -> Result<QueryCtx, Self::Err> {
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
                "ID" => Id::from_str(v).map(|id| QueryCtx {
                    key: QueryKey::ID(id),
                    modifiers: mods,
                }),
                _ => Err(Error::InvalidQueryType),
            },
        }
    }
}

pub type AircraftVariants = HashMap<Priority, Rc<Aircraft>>;

// TODO: implement IntoIterator returning by_id
#[derive(Debug, Clone)]
pub struct Aircrafts {
    pub by_id: HashMap<Id, AircraftVariants>,
    pub by_shortname: HashMap<ShortName, AircraftVariants>,
    pub by_name: HashMap<Name, AircraftVariants>,
}

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
        // TODO: HashMap<*, Rc<RefCell<AircraftVariants>>> looks ugly...
        //        id ---> AircraftVariants[priority] ---> Aircraft
        // shortname --/
        //      name -/
        let ac = Rc::new(aircraft);

        self.by_id
            .entry(ac.id.clone())
            .or_default()
            .insert(ac.priority.clone(), Rc::clone(&ac));

        self.by_shortname
            .entry(ShortName(ac.shortname.0.to_uppercase()))
            .or_default()
            .insert(ac.priority.clone(), Rc::clone(&ac));

        self.by_name
            .entry(Name(ac.name.0.to_uppercase()))
            .or_default()
            .insert(ac.priority.clone(), Rc::clone(&ac));
    }
}

#[derive(Debug)]
pub struct CustomAircraft {
    pub aircraft: Rc<Aircraft>,
    pub modifiers: Modifiers,
}

impl CustomAircraft {
    pub fn new(aircraft: Rc<Aircraft>, modifiers: Modifiers) -> Self {
        let mut mulspd: f32 = 1.0;
        let mut mulfuel: f32 = 1.0;
        let mut mulco2: f32 = 1.0;
        let mut mulcost: f32 = 1.0;

        if modifiers.speed_mod {
            mulspd *= 1.1;
            mulcost *= 1.07;
        }
        if modifiers.fuel_mod {
            mulfuel *= 0.9;
            mulcost *= 1.10;
        }
        if modifiers.co2_mod {
            mulco2 *= 0.9;
            mulcost *= 1.05;
        }
        if modifiers.fourx_mod {
            mulspd *= 4.0;
        }
        if modifiers.easy_boost {
            mulspd *= 1.5;
        }

        let ac = if mulspd == 1.0 && mulfuel == 1.0 && mulco2 == 1.0 && mulcost == 1.0 {
            aircraft
        } else {
            let mut cloned = (*aircraft).clone();
            cloned.speed *= mulspd;
            cloned.fuel *= mulfuel;
            cloned.co2 *= mulco2;
            cloned.cost = (cloned.cost as f32 * mulcost).ceil() as u32;
            Rc::new(cloned)
        };

        Self {
            aircraft: ac,
            modifiers,
        }
    }
}

impl Aircrafts {
    pub fn search(&self, s: &str) -> Result<CustomAircraft, Error> {
        let ctx = QueryCtx::from_str(s)?;

        let ac = self.search_variants_(&ctx)?;
        ac.get(&ctx.modifiers.priority)
            .map(|ac| CustomAircraft::new(Rc::clone(ac), ctx.modifiers))
            .ok_or(Error::AircraftPriorityNotFound)
    }

    pub fn search_variants(&self, s: &str) -> Result<&AircraftVariants, Error> {
        let ctx = QueryCtx::from_str(s)?;
        self.search_variants_(&ctx)
    }

    fn search_variants_(&self, ctx: &QueryCtx) -> Result<&AircraftVariants, Error> {
        match &ctx.key {
            QueryKey::ALL(s) => {
                if let Ok(id) = Id::from_str(s) {
                    self.by_id.get(&id)
                } else if let Some(ac) = self.by_shortname.get(&ShortName(s.to_uppercase())) {
                    Some(ac)
                } else {
                    self.by_name.get(&Name(s.to_uppercase()))
                }
            }
            QueryKey::ID(id) => self.by_id.get(id),
            QueryKey::SHORTNAME(sn) => self.by_shortname.get(sn),
            QueryKey::NAME(name) => self.by_name.get(name),
        }
        .ok_or(Error::AircraftNotFound)
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
    } else if similarity > heap.peek().unwrap().similarity {
        heap.pop();
        heap.push(Suggestion::<Rc<Aircraft>> {
            item: Rc::clone(aircraft),
            similarity,
        });
    }
}

impl Aircrafts {
    pub fn suggest(&self, s: &str) -> Vec<Suggestion<Rc<Aircraft>>> {
        let su = s.to_uppercase();

        let mut heap = BinaryHeap::with_capacity(MAX_SUGGESTIONS);

        for (k, ac_variants) in &self.by_shortname {
            if let Some(aircraft) = ac_variants.values().next() {
                queue_suggestions(&mut heap, aircraft, jaro_winkler(&k.0, &su));
            }
        }
        for (k, ac_variants) in &self.by_name {
            if let Some(aircraft) = ac_variants.values().next() {
                queue_suggestions(&mut heap, aircraft, jaro_winkler(&k.0, &su));
            }
        }

        heap.into_sorted_vec()
    }
}

#[derive(Debug, Error)]
pub enum Error {
    #[error("Invalid aircraft ID: {0}")]
    InvalidID(#[source] std::num::ParseIntError),
    #[error("Invalid query type")]
    InvalidQueryType,
    #[error("Aircraft not found")]
    AircraftNotFound,
    #[error("Aircraft priority not found")]
    AircraftPriorityNotFound,
    #[error("Invalid aircraft type")]
    InvalidAircraftType,
    #[error("Invalid engine priority: {0}")]
    InvalidEnginePriority(#[source] std::num::ParseIntError),
    #[error("Invalid modifier: {0}")]
    InvalidModifier(String),
}
