use crate::demand::pax::PaxDemand;
use crate::user::GameMode;

pub struct PaxConfig {
    pub y: u16,
    pub j: u16,
    pub f: u16,
    pub algorithm: PaxConfigAlgorithm,
}

pub enum PaxConfigAlgorithm {
    Auto,
    Fjy,
    Fyj,
    Jfy,
    Jyf,
    Yfj,
    Yjf,
}

impl PaxConfig {
    fn calc_fjy_conf(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let f = std::cmp::min(d_pf.f, (remaining_capacity / 3) as u16);
        remaining_capacity -= (f * 3) as u16;

        let j = std::cmp::min(d_pf.j, (remaining_capacity / 2) as u16);
        remaining_capacity -= (j * 2) as u16;

        let y = remaining_capacity as u16;

        if y < d_pf.y {
            Some(PaxConfig {
                f,
                j,
                y,
                algorithm: PaxConfigAlgorithm::Fjy,
            })
        } else {
            None
        }
    }

    fn calc_fyj_conf(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let f = std::cmp::min(d_pf.f, (remaining_capacity / 3) as u16);
        remaining_capacity -= (f * 3) as u16;

        let y = std::cmp::min(d_pf.y, remaining_capacity as u16);
        remaining_capacity -= y as u16;

        let j = (remaining_capacity / 2) as u16;

        if j < d_pf.j {
            Some(PaxConfig {
                f,
                j,
                y,
                algorithm: PaxConfigAlgorithm::Fyj,
            })
        } else {
            None
        }
    }

    fn calc_jfy_conf(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let j = std::cmp::min(d_pf.j, (remaining_capacity / 2) as u16);
        remaining_capacity -= (j * 2) as u16;

        let f = std::cmp::min(d_pf.f, (remaining_capacity / 3) as u16);
        remaining_capacity -= (f * 3) as u16;

        let y = remaining_capacity as u16;

        if y < d_pf.y {
            Some(PaxConfig {
                f,
                j,
                y,
                algorithm: PaxConfigAlgorithm::Jfy,
            })
        } else {
            None
        }
    }

    fn calc_jyf_conf(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let j = std::cmp::min(d_pf.j, (remaining_capacity / 2) as u16);
        remaining_capacity -= (j * 2) as u16;

        let y = std::cmp::min(d_pf.y, remaining_capacity as u16);
        remaining_capacity -= y as u16;

        let f = (remaining_capacity / 3) as u16;

        if f < d_pf.f {
            Some(PaxConfig {
                f,
                j,
                y,
                algorithm: PaxConfigAlgorithm::Jyf,
            })
        } else {
            None
        }
    }

    fn calc_yfj_conf(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let y = std::cmp::min(d_pf.y, remaining_capacity as u16);
        remaining_capacity -= y as u16;

        let f = std::cmp::min(d_pf.f, (remaining_capacity / 3) as u16);
        remaining_capacity -= (f * 3) as u16;

        let j = (remaining_capacity / 2) as u16;

        if j < d_pf.j {
            Some(PaxConfig {
                f,
                j,
                y,
                algorithm: PaxConfigAlgorithm::Yfj,
            })
        } else {
            None
        }
    }

    fn calc_yjf_conf(d_pf: &PaxDemand, capacity: u16) -> Option<Self> {
        let mut remaining_capacity = capacity;

        let y = std::cmp::min(d_pf.y, remaining_capacity as u16);
        remaining_capacity -= y as u16;

        let j = std::cmp::min(d_pf.j, (remaining_capacity / 2) as u16);
        remaining_capacity -= (j * 2) as u16;

        let f = (remaining_capacity / 3) as u16;

        if f < d_pf.f {
            Some(PaxConfig {
                f,
                j,
                y,
                algorithm: PaxConfigAlgorithm::Yjf,
            })
        } else {
            None
        }
    }

    pub fn calculate_pax_config(
        d_pf: &PaxDemand,
        capacity: u16,
        distance: u32,
        game_mode: GameMode,
        algorithm: PaxConfigAlgorithm,
    ) -> Option<PaxConfig> {
        match algorithm {
            PaxConfigAlgorithm::Auto => match game_mode {
                GameMode::Easy => {
                    if distance < 14425 {
                        Self::calc_fjy_conf(d_pf, capacity)
                    } else if distance < 14812 {
                        Self::calc_fyj_conf(d_pf, capacity)
                    } else if distance < 15200 {
                        Self::calc_yfj_conf(d_pf, capacity)
                    } else {
                        Self::calc_yjf_conf(d_pf, capacity)
                    }
                }
                GameMode::Realism => {
                    if distance < 13888 {
                        Self::calc_fjy_conf(d_pf, capacity)
                    } else if distance < 15694 {
                        Self::calc_jfy_conf(d_pf, capacity)
                    } else if distance < 17500 {
                        Self::calc_jyf_conf(d_pf, capacity)
                    } else {
                        Self::calc_yjf_conf(d_pf, capacity)
                    }
                }
            },
            PaxConfigAlgorithm::Fjy => Self::calc_fjy_conf(d_pf, capacity),
            PaxConfigAlgorithm::Fyj => Self::calc_fyj_conf(d_pf, capacity),
            PaxConfigAlgorithm::Jfy => Self::calc_jfy_conf(d_pf, capacity),
            PaxConfigAlgorithm::Jyf => Self::calc_jyf_conf(d_pf, capacity),
            PaxConfigAlgorithm::Yfj => Self::calc_yfj_conf(d_pf, capacity),
            PaxConfigAlgorithm::Yjf => Self::calc_yjf_conf(d_pf, capacity),
        }
    }
}
