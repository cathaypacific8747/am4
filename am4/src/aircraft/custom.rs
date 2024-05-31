use crate::aircraft::EnginePriority;
use crate::aircraft::{Aircraft, AircraftError};
use std::collections::HashSet;
use std::str::FromStr;

#[derive(Debug)]
pub struct CustomAircraft {
    pub aircraft: Aircraft,
    pub modifiers: Modification,
}

#[derive(Debug)]
pub struct Modification {
    pub mods: HashSet<Modifier>, // not using Vec to avoid duplicates
    pub engine: EnginePriority,
}

#[derive(Debug, PartialEq, Eq, Hash)]
pub enum Modifier {
    Speed,
    Fuel,
    Co2,
    FourX,
    EasyBoost,
}

impl CustomAircraft {
    pub fn from_aircraft_and_modifiers(aircraft: Aircraft, modifiers: Modification) -> Self {
        let mut ac = aircraft;
        let mut cost_mul = 1.0;

        for modifier in modifiers.mods.iter() {
            modifier.apply(&mut ac);
            cost_mul *= modifier.cost_multiplier();
        }
        ac.cost = (ac.cost as f32 * cost_mul).ceil() as u32;

        Self {
            aircraft: ac,
            modifiers,
        }
    }
}

impl Modifier {
    fn apply(&self, aircraft: &mut Aircraft) {
        match self {
            Modifier::Speed => aircraft.speed *= 1.1,
            Modifier::Fuel => aircraft.fuel *= 0.9,
            Modifier::Co2 => aircraft.co2 *= 0.9,
            Modifier::FourX => aircraft.speed *= 4.0,
            Modifier::EasyBoost => aircraft.speed *= 1.5,
        }
    }

    fn cost_multiplier(&self) -> f32 {
        match self {
            Modifier::Speed => 1.07,
            Modifier::Fuel => 1.10,
            Modifier::Co2 => 1.05,
            Modifier::FourX | Modifier::EasyBoost => 1.0,
        }
    }
}

impl Default for Modification {
    fn default() -> Self {
        Modification {
            mods: HashSet::new(),
            engine: EnginePriority(0),
        }
    }
}

impl FromStr for Modification {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Modification, Self::Err> {
        let mut modifi = Modification::default();

        for c in s.to_lowercase().chars() {
            match c {
                's' => modifi.mods.insert(Modifier::Speed),
                'f' => modifi.mods.insert(Modifier::Fuel),
                'c' => modifi.mods.insert(Modifier::Co2),
                'x' => modifi.mods.insert(Modifier::FourX),
                'e' => modifi.mods.insert(Modifier::EasyBoost),
                ' ' | ',' => continue,
                p => {
                    modifi.engine = EnginePriority::from_str(&p.to_string())?;
                    true // just to match the return type of insert
                }
            };
        }

        Ok(modifi)
    }
}
