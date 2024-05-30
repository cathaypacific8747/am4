#[derive(Debug, Clone, PartialEq, Copy)]
pub enum Airline {
    C4_4HR,
    C4_8HR,
    C4_12HR,
    C4_16HR,
    C4_20HR,
    C4_24HR,
    C3_4HR,
    C3_8HR,
    C3_12HR,
    C3_16HR,
    C3_20HR,
    C3_24HR,
    C2_4HR,
    C2_8HR,
    C2_12HR,
    C2_16HR,
    C2_20HR,
    C2_24HR,
    C1_4HR,
    C1_8HR,
    C1_12HR,
    C1_16HR,
    C1_20HR,
    C1_24HR,
    None,
}

impl Default for Airline {
    fn default() -> Self {
        Self::None
    }
}

#[derive(Debug, Clone, PartialEq, Copy)]
pub enum Eco {
    C4Hr,
    C8Hr,
    C12Hr,
    C16Hr,
    C20Hr,
    C24Hr,
    None,
}

impl Default for Eco {
    fn default() -> Self {
        Self::None
    }
}

#[derive(Debug, Clone, Default)]
pub struct Campaign {
    pub pax_activated: Airline,
    pub cargo_activated: Airline,
    pub eco_activated: Eco,
}

impl Campaign {
    pub fn new(pax_activated: Airline, cargo_activated: Airline, eco_activated: Eco) -> Self {
        Self {
            pax_activated,
            cargo_activated,
            eco_activated,
        }
    }

    pub fn estimate_pax_reputation(&self, base_reputation: f64) -> f64 {
        let mut reputation = base_reputation;
        reputation += self.estimate_airline_reputation(self.pax_activated);
        reputation += self.estimate_eco_reputation(self.eco_activated);
        reputation
    }

    pub fn estimate_cargo_reputation(&self, base_reputation: f64) -> f64 {
        let mut reputation = base_reputation;
        reputation += self.estimate_airline_reputation(self.cargo_activated);
        reputation += self.estimate_eco_reputation(self.eco_activated);
        reputation
    }

    fn estimate_airline_reputation(&self, airline: Airline) -> f64 {
        match airline {
            Airline::C4_4HR
            | Airline::C4_8HR
            | Airline::C4_12HR
            | Airline::C4_16HR
            | Airline::C4_20HR
            | Airline::C4_24HR => 30.0,
            Airline::C3_4HR
            | Airline::C3_8HR
            | Airline::C3_12HR
            | Airline::C3_16HR
            | Airline::C3_20HR
            | Airline::C3_24HR => 21.5,
            Airline::C2_4HR
            | Airline::C2_8HR
            | Airline::C2_12HR
            | Airline::C2_16HR
            | Airline::C2_20HR
            | Airline::C2_24HR => 14.0,
            Airline::C1_4HR
            | Airline::C1_8HR
            | Airline::C1_12HR
            | Airline::C1_16HR
            | Airline::C1_20HR
            | Airline::C1_24HR => 7.5,
            Airline::None => 0.0,
        }
    }

    fn estimate_eco_reputation(&self, eco: Eco) -> f64 {
        match eco {
            Eco::C4Hr | Eco::C8Hr | Eco::C12Hr | Eco::C16Hr | Eco::C20Hr | Eco::C24Hr => 10.0,
            Eco::None => 0.0,
        }
    }

    fn set(&mut self, s: &str) -> bool {
        match s.to_ascii_uppercase().as_str() {
            "C1" => {
                self.pax_activated = Airline::C1_24HR;
                self.cargo_activated = Airline::C1_24HR;
                true
            }
            "C2" => {
                self.pax_activated = Airline::C2_24HR;
                self.cargo_activated = Airline::C2_24HR;
                true
            }
            "C3" => {
                self.pax_activated = Airline::C3_24HR;
                self.cargo_activated = Airline::C3_24HR;
                true
            }
            "C4" => {
                self.pax_activated = Airline::C4_24HR;
                self.cargo_activated = Airline::C4_24HR;
                true
            }
            "E" => {
                self.eco_activated = Eco::C24Hr;
                true
            }
            _ => false,
        }
    }

    pub fn parse(s: &str) -> Self {
        let mut campaign = Self::default();
        let s_upper = s.replace(' ', "");
        if s_upper.is_empty() {
            return campaign;
        }

        if let Some(pos) = s_upper.find(',') {
            campaign.set(&s_upper[..pos]);
            campaign.set(&s_upper[pos + 1..]);
        } else {
            campaign.set(&s_upper);
        }
        campaign
    }
}
