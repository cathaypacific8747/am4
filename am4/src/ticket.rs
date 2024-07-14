use crate::user::GameMode;

#[derive(Debug)]
pub struct PaxTicket {
    pub y: u16,
    pub j: u16,
    pub f: u16,
}

impl PaxTicket {
    pub fn from_optimal(distance: f64, game_mode: GameMode) -> Self {
        let (y, j, f) = if game_mode == GameMode::Easy {
            (
                (1.10 * (0.4 * distance + 170.0) - 2.0) as u16,
                (1.08 * (0.8 * distance + 560.0) - 2.0) as u16,
                (1.06 * (1.2 * distance + 1200.0) - 2.0) as u16,
            )
        } else {
            (
                (1.10 * (0.3 * distance + 150.0) - 2.0) as u16,
                (1.08 * (0.6 * distance + 500.0) - 2.0) as u16,
                (1.06 * (0.9 * distance + 1000.0) - 2.0) as u16,
            )
        };
        Self { y, j, f }
    }
}

#[derive(Debug)]
pub struct CargoTicket {
    pub l: f32,
    pub h: f32,
}

impl CargoTicket {
    pub fn from_optimal(distance: f64, game_mode: GameMode) -> Self {
        match game_mode {
            GameMode::Easy => Self {
                l: (1.10 * (0.0948283724581252 * distance + 85.2045432642377)).floor() as f32
                    / 100.0,
                h: (1.08 * (0.0689663577640275 * distance + 28.2981124272893)).floor() as f32
                    / 100.0,
            },
            GameMode::Realism => Self {
                l: (1.10 * (0.0776321822039374 * distance + 85.0567600367807)).floor() as f32
                    / 100.0,
                h: (1.08 * (0.0517742799409248 * distance + 24.6369915396414)).floor() as f32
                    / 100.0,
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
