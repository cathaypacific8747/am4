// TODO: use C*(num_hours) instead

use derive_more::{Display, Into};
use std::str::FromStr;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum CampaignError {
    #[error("Campaign duration must be 4, 8, 12, 16, 20 or 24 hours.")]
    InvalidDuration,
}

#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Into, Display)]
pub struct Duration(u8);

impl TryFrom<u8> for Duration {
    type Error = CampaignError;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        match value {
            4 | 8 | 12 | 16 | 20 | 24 => Ok(Self(value)),
            _ => Err(CampaignError::InvalidDuration),
        }
    }
}

impl Duration {
    pub const FOUR: Self = Self(4);
    pub const EIGHT: Self = Self(8);
    pub const TWELVE: Self = Self(12);
    pub const SIXTEEN: Self = Self(16);
    pub const TWENTY: Self = Self(20);
    pub const TWENTYFOUR: Self = Self(24);
}

pub type Reputation = f32;

pub trait ReputationBoost {
    fn reputation_boost(&self) -> Reputation;
}

#[derive(Debug, Clone, PartialEq, Default)]
pub enum Airline {
    #[default]
    None,
    C1(Duration),
    C2(Duration),
    C3(Duration),
    C4(Duration),
}

impl ReputationBoost for Airline {
    fn reputation_boost(&self) -> Reputation {
        match self {
            Self::None => 0.0,
            Self::C1(_) => 7.5,
            Self::C2(_) => 14.0,
            Self::C3(_) => 21.5,
            Self::C4(_) => 30.0,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Default)]
pub enum Eco {
    #[default]
    None,
    Activated(Duration),
}

impl ReputationBoost for Eco {
    fn reputation_boost(&self) -> Reputation {
        match self {
            Self::None => 0.0,
            Self::Activated(_) => 10.0,
        }
    }
}

#[derive(Debug, Default)]
pub struct Campaign {
    pub pax: Airline,
    pub cargo: Airline,
    pub charter: Airline,
    pub eco: Eco,
}

impl Campaign {
    pub fn reputation_pax(&self, base: Reputation) -> Reputation {
        base + self.pax.reputation_boost() + self.eco.reputation_boost()
    }

    pub fn reputation_cargo(&self, base: Reputation) -> Reputation {
        base + self.cargo.reputation_boost() + self.eco.reputation_boost()
    }

    pub fn reputation_charter(&self, base: Reputation) -> Reputation {
        base + self.charter.reputation_boost() + self.eco.reputation_boost()
    }

    fn set(&mut self, s: &str) -> bool {
        let full = Duration::TWENTYFOUR;
        match s.to_ascii_uppercase().as_str() {
            "C1" => {
                self.pax = Airline::C1(full);
                self.cargo = Airline::C1(full);
                self.charter = Airline::C1(full);
                true
            }
            "C2" => {
                self.pax = Airline::C2(full);
                self.cargo = Airline::C2(full);
                self.charter = Airline::C2(full);
                true
            }
            "C3" => {
                self.pax = Airline::C3(full);
                self.cargo = Airline::C3(full);
                self.charter = Airline::C3(full);
                true
            }
            "C4" => {
                self.pax = Airline::C4(full);
                self.cargo = Airline::C4(full);
                self.charter = Airline::C4(full);
                true
            }
            "E" => {
                self.eco = Eco::Activated(full);
                true
            }
            _ => false,
        }
    }
}

// TODO: use nom
impl FromStr for Campaign {
    type Err = CampaignError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let mut campaign = Campaign::default();
        let s_upper = s.replace(' ', "");
        if s_upper.is_empty() {
            return Ok(campaign);
        }

        if let Some(pos) = s_upper.find(',') {
            campaign.set(&s_upper[..pos]);
            campaign.set(&s_upper[pos + 1..]);
        } else {
            campaign.set(&s_upper);
        }
        Ok(campaign)
    }
}
#[test]
fn test_campaign() {
    let c = Campaign::from_str("c1, e").unwrap();
    assert_eq!(c.pax, Airline::C1(Duration::TWENTYFOUR));
    assert_eq!(c.cargo, Airline::C1(Duration::TWENTYFOUR));
    assert_eq!(c.eco, Eco::Activated(Duration::TWENTYFOUR));

    let c = Campaign::from_str("e").unwrap();
    assert_eq!(c.pax, Airline::None);
    assert_eq!(c.cargo, Airline::None);
    assert_eq!(c.eco, Eco::Activated(Duration::TWENTYFOUR));
}

#[test]
fn test_campaign_reputation() {
    const REPUTATION_BASE: f32 = 45.0;

    let c = Campaign::from_str("e").unwrap();
    let rep = c.reputation_pax(REPUTATION_BASE);
    assert_eq!(rep, REPUTATION_BASE + 10.0);

    let c = Campaign::from_str("c1, e").unwrap();
    let rep = c.reputation_pax(REPUTATION_BASE);
    assert_eq!(rep, REPUTATION_BASE + 7.5 + 10.0);

    let c = Campaign::from_str("c4, e").unwrap();
    let rep = c.reputation_pax(REPUTATION_BASE);
    assert_eq!(rep, REPUTATION_BASE + 30.0 + 10.0);
}
