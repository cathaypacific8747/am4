use crate::route::demand::CargoDemand;
use crate::route::demand::PaxDemand;

#[derive(Debug)]
pub struct CargoConfig {
    pub l: u8,
    pub h: u8,
    pub algorithm: CargoConfigAlgorithm,
}

#[derive(Debug, Default)]
pub enum CargoConfigAlgorithm {
    #[default]
    Auto,
    L,
    H,
}

impl CargoConfig {
    fn calc_l_conf(
        d_pf: &PaxDemand,
        capacity: u32,
        l_training: u8,
        h_training: u8,
    ) -> Option<Self> {
        let d_pf_cargo = CargoDemand::from(d_pf);

        let l_cap = capacity as f32 * 0.7 * (1.0 + l_training as f32 / 100.0);

        if d_pf_cargo.l as f32 > l_cap {
            return Some(CargoConfig {
                l: 100,
                h: 0,
                algorithm: CargoConfigAlgorithm::L,
            });
        }

        let l = d_pf_cargo.l as f32 / l_cap;
        let h = 1. - l;
        if (d_pf_cargo.h as f32) < capacity as f32 * h * (1.0 + h_training as f32 / 100.0) {
            None
        } else {
            let lu = (l * 100.0) as u8;

            Some(CargoConfig {
                l: lu,
                h: 100 - lu,
                algorithm: CargoConfigAlgorithm::L,
            })
        }
    }

    fn calc_h_conf(
        d_pf: &PaxDemand,
        capacity: u32,
        l_training: u8,
        h_training: u8,
    ) -> Option<Self> {
        let d_pf_cargo = CargoDemand::from(d_pf);

        let h_cap = capacity as f32 * (1.0 + h_training as f32 / 100.0);

        if d_pf_cargo.h as f32 > h_cap {
            return Some(CargoConfig {
                l: 0,
                h: 100,
                algorithm: CargoConfigAlgorithm::H,
            });
        }

        let h = d_pf_cargo.h as f32 / h_cap;
        let l = 1. - h;
        if (d_pf_cargo.l as f32) < capacity as f32 * l * 0.7 * (1.0 + l_training as f32 / 100.0) {
            None
        } else {
            let hu = (h * 100.0) as u8;

            Some(CargoConfig {
                l: 100 - hu,
                h: hu,
                algorithm: CargoConfigAlgorithm::H,
            })
        }
    }

    // Implements a greedy configuration algorithm for cargo aircraft.
    pub fn calculate_cargo_config(
        d_pf: &PaxDemand,
        capacity: u32,
        l_training: u8,
        h_training: u8,
        algorithm: CargoConfigAlgorithm,
    ) -> Option<Self> {
        match algorithm {
            CargoConfigAlgorithm::Auto | CargoConfigAlgorithm::L => {
                Self::calc_l_conf(d_pf, capacity, l_training, h_training)
            }
            CargoConfigAlgorithm::H => Self::calc_h_conf(d_pf, capacity, l_training, h_training),
        }
    }
}
