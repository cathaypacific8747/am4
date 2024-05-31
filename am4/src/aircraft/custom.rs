use crate::aircraft::Aircraft;
use crate::aircraft::Priority;

#[derive(Debug)]
pub struct CustomAircraft {
    pub aircraft: Aircraft,
    pub modifiers: Modifiers,
}

impl CustomAircraft {
    pub fn from_aircraft_and_modifiers(aircraft: Aircraft, modifiers: Modifiers) -> Self {
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

        let mut ac = aircraft.clone();
        ac.speed *= mulspd;
        ac.fuel *= mulfuel;
        ac.co2 *= mulco2;
        ac.cost = (ac.cost as f32 * mulcost).ceil() as u32;

        Self {
            aircraft: ac,
            modifiers,
        }
    }
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
