#![allow(clippy::excessive_precision)]
use crate::user::GameMode;

#[derive(Debug)]
pub struct PaxTicket {
    pub y: u16,
    pub j: u16,
    pub f: u16,
}

impl PaxTicket {
    fn base_easy(distance: f32) -> (f32, f32, f32) {
        (
            0.4 * distance + 170.0,
            0.8 * distance + 560.0,
            1.2 * distance + 1200.0,
        )
    }

    fn base_realism(distance: f32) -> (f32, f32, f32) {
        (
            0.3 * distance + 150.0,
            0.6 * distance + 500.0,
            0.9 * distance + 1000.0,
        )
    }

    fn make_optimal((y, j, f): (f32, f32, f32)) -> Self {
        Self {
            y: (1.10 * y) as u16 - 2,
            j: (1.08 * j) as u16 - 2,
            f: (1.06 * f) as u16 - 2,
        }
    }

    pub fn from_optimal(distance: f32, game_mode: &GameMode) -> Self {
        PaxTicket::make_optimal(match game_mode {
            GameMode::Easy => PaxTicket::base_easy(distance),
            GameMode::Realism => PaxTicket::base_realism(distance),
        })
    }
}

#[derive(Debug)]
pub struct CargoTicket {
    pub l: f32,
    pub h: f32,
}

// TODO: refactor
impl CargoTicket {
    pub fn from_optimal(distance: f32, game_mode: GameMode) -> Self {
        match game_mode {
            GameMode::Easy => Self {
                l: (1.10 * (0.0948283724581252 * distance + 85.2045432642377)).floor() / 100.0,
                h: (1.08 * (0.0689663577640275 * distance + 28.2981124272893)).floor() / 100.0,
            },
            GameMode::Realism => Self {
                l: (1.10 * (0.0776321822039374 * distance + 85.0567600367807)).floor() / 100.0,
                h: (1.08 * (0.0517742799409248 * distance + 24.6369915396414)).floor() / 100.0,
            },
        }
    }
}

#[derive(Debug)]
pub struct VIPTicket {
    pub y: u16,
    pub j: u16,
    pub f: u16,
}

impl VIPTicket {
    pub fn from_optimal(distance: f64) -> Self {
        let y = (1.22 * 1.7489 * (0.4 * distance + 170.0) - 2.0) as u16;
        let j = (1.20 * 1.7489 * (0.8 * distance + 560.0) - 2.0) as u16;
        let f = (1.17 * 1.7489 * (1.2 * distance + 1200.0) - 2.0) as u16;
        Self { y, j, f }
    }
}

#[derive(Debug)]
pub enum Ticket {
    Pax(PaxTicket),
    Cargo(CargoTicket),
    VIP(VIPTicket),
}
