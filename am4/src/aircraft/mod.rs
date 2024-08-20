pub mod custom;
pub mod db;

use derive_more::{Constructor, Display, From, Into};
use std::str::FromStr;
use thiserror::Error;

#[cfg(feature = "rkyv")]
use rkyv::{Archive as Ra, Deserialize as Rd, Serialize as Rs};
#[cfg(feature = "serde")]
use serde::Deserialize;

#[derive(Debug, Clone, PartialEq)]
#[cfg_attr(feature = "rkyv", derive(Ra, Rd, Rs), archive(check_bytes))]
#[cfg_attr(feature = "serde", derive(Deserialize))]
pub struct Aircraft {
    pub id: Id,
    pub shortname: ShortName,
    pub manufacturer: String,
    pub name: Name,
    pub r#type: AircraftType,
    pub priority: EnginePriority,
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

#[derive(Debug, Clone, Copy, Display, PartialEq, Eq, Hash, Constructor, Into)]
#[cfg_attr(feature = "rkyv", derive(Ra, Rd, Rs), archive(check_bytes))]
#[cfg_attr(feature = "serde", derive(Deserialize))]
pub struct Id(u16);

impl FromStr for Id {
    type Err = AircraftError;

    fn from_str(id: &str) -> Result<Self, Self::Err> {
        id.parse::<u16>()
            .map(Self)
            .map_err(AircraftError::InvalidID)
    }
}

#[derive(Debug, Clone, Display, PartialEq, Eq, Hash, Into)]
#[cfg_attr(feature = "rkyv", derive(Ra, Rd, Rs), archive(check_bytes))]
#[cfg_attr(feature = "serde", derive(Deserialize))]
pub struct ShortName(String);

impl FromStr for ShortName {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.len() {
            1..=20 => Ok(Self(s.to_string())), // actual max 11, but not invalidating because we want fuzzy search to not be too strict
            _ => Err(AircraftError::InvalidShortName),
        }
    }
}

#[derive(Debug, Clone, Display, PartialEq, Eq, Hash, Into)]
#[cfg_attr(feature = "rkyv", derive(Ra, Rd, Rs), archive(check_bytes))]
#[cfg_attr(feature = "serde", derive(Deserialize))]
pub struct Name(String);

impl FromStr for Name {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.len() {
            1..=40 => Ok(Self(s.to_string())), // actual max 28
            _ => Err(AircraftError::InvalidName),
        }
    }
}

#[derive(Debug, Clone, Copy, Display, PartialEq, Eq, Hash, Constructor, Into, From)]
#[cfg_attr(feature = "rkyv", derive(Ra, Rd, Rs), archive(check_bytes))]
#[cfg_attr(feature = "serde", derive(Deserialize))]
pub struct EnginePriority(u8);

impl FromStr for EnginePriority {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        s.parse::<u8>()
            .map(Self)
            .map_err(AircraftError::InvalidPriority)
    }
}

#[derive(Debug, Clone, Display, PartialEq)]
#[cfg_attr(feature = "rkyv", derive(Ra, Rd, Rs), archive(check_bytes))]
#[cfg_attr(
    feature = "serde",
    derive(Deserialize),
    serde(rename_all = "lowercase")
)]
pub enum AircraftType {
    Pax,
    Cargo,
    #[display("VIP")]
    Vip,
}

impl FromStr for AircraftType {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "PAX" => Ok(Self::Pax),
            "CARGO" => Ok(Self::Cargo),
            "VIP" => Ok(Self::Vip),
            _ => Err(AircraftError::InvalidAircraftType),
        }
    }
}

// TODO: wrap ParseIntError and manually derive serde and rkyv
#[derive(Debug, Error)]
pub enum AircraftError {
    #[error("Invalid aircraft ID: {0}")]
    InvalidID(#[source] std::num::ParseIntError),
    #[error("Invalid short name: must be between 1 and 20 characters")]
    InvalidShortName,
    #[error("Invalid name: must be between 1 and 40 characters")]
    InvalidName,
    #[error("Invalid aircraft type")]
    InvalidAircraftType,
    #[error("Invalid engine priority: {0}")]
    InvalidPriority(#[source] std::num::ParseIntError),
}
