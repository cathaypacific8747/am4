use crate::route::demand::PaxDemand;
use crate::user::GameMode;
use std::cmp::min;

#[derive(Debug)]
pub struct PaxConfig {
    pub y: u16,
    pub j: u16,
    pub f: u16,
}

#[derive(Debug, Default)]
pub enum PaxConfigAlgorithm {
    #[default]
    Auto,
    Fjy,
    Fyj,
    Jfy,
    Jyf,
    Yfj,
    Yjf,
}

impl PaxConfig {
    /// Implements a greedy configuration algorithm for pax aircraft.
    /// Returns None if demand is exhausted.
    pub fn calculate_pax_config(
        d_pf: &PaxDemand,
        capacity: u16,
        distance: f32,
        game_mode: &GameMode,
        algorithm: &PaxConfigAlgorithm,
    ) -> Option<PaxConfig> {
        match algorithm {
            PaxConfigAlgorithm::Auto => match game_mode {
                GameMode::Easy => {
                    if distance < 14425. {
                        Self::from_fjy(d_pf, capacity)
                    } else if distance < 14812. {
                        Self::from_fyj(d_pf, capacity)
                    } else if distance < 15200. {
                        Self::from_yfj(d_pf, capacity)
                    } else {
                        Self::from_yjf(d_pf, capacity)
                    }
                }
                GameMode::Realism => {
                    if distance < 13888.889 {
                        Self::from_fjy(d_pf, capacity)
                    } else if distance < 15694.444 {
                        Self::from_jfy(d_pf, capacity)
                    } else if distance < 17500. {
                        Self::from_jyf(d_pf, capacity)
                    } else {
                        Self::from_yjf(d_pf, capacity)
                    }
                }
            },
            PaxConfigAlgorithm::Fjy => Self::from_fjy(d_pf, capacity),
            PaxConfigAlgorithm::Fyj => Self::from_fyj(d_pf, capacity),
            PaxConfigAlgorithm::Jfy => Self::from_jfy(d_pf, capacity),
            PaxConfigAlgorithm::Jyf => Self::from_jyf(d_pf, capacity),
            PaxConfigAlgorithm::Yfj => Self::from_yfj(d_pf, capacity),
            PaxConfigAlgorithm::Yjf => Self::from_yjf(d_pf, capacity),
        }
    }

    fn from_fjy(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let f = min(d_pf.f, remaining_capacity / 3);
        remaining_capacity -= f * 3;

        let j = min(d_pf.j, remaining_capacity / 2);
        remaining_capacity -= j * 2;

        let y = remaining_capacity;

        if y < d_pf.y {
            Some(PaxConfig { f, j, y })
        } else {
            None
        }
    }

    fn from_fyj(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let f = min(d_pf.f, remaining_capacity / 3);
        remaining_capacity -= f * 3;

        let y = min(d_pf.y, remaining_capacity);
        remaining_capacity -= y;

        let j = remaining_capacity / 2;

        if j < d_pf.j {
            Some(PaxConfig { f, y, j })
        } else {
            None
        }
    }

    fn from_jfy(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let j = min(d_pf.j, remaining_capacity / 2);
        remaining_capacity -= j * 2;

        let f = min(d_pf.f, remaining_capacity / 3);
        remaining_capacity -= f * 3;

        let y = remaining_capacity;

        if y < d_pf.y {
            Some(PaxConfig { j, f, y })
        } else {
            None
        }
    }

    fn from_jyf(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let j = min(d_pf.j, remaining_capacity / 2);
        remaining_capacity -= j * 2;

        let y = min(d_pf.y, remaining_capacity);
        remaining_capacity -= y;

        let f = remaining_capacity / 3;

        if f < d_pf.f {
            Some(PaxConfig { j, y, f })
        } else {
            None
        }
    }

    fn from_yfj(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let y = min(d_pf.y, remaining_capacity);
        remaining_capacity -= y;

        let f = min(d_pf.f, remaining_capacity / 3);
        remaining_capacity -= f * 3;

        let j = remaining_capacity / 2;

        if j < d_pf.j {
            Some(PaxConfig { y, f, j })
        } else {
            None
        }
    }

    fn from_yjf(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let y = min(d_pf.y, remaining_capacity);
        remaining_capacity -= y;

        let j = min(d_pf.j, remaining_capacity / 2);
        remaining_capacity -= j * 2;

        let f = remaining_capacity / 3;

        if f < d_pf.f {
            Some(PaxConfig { y, j, f })
        } else {
            None
        }
    }
}
