//! Implements greedy configuration algorithms for pax and cargo aircraft

mod cargo;
mod pax;

pub use cargo::{CargoConfig, CargoConfigAlgorithm};
pub use pax::{PaxConfig, PaxConfigAlgorithm};

#[derive(Debug)]
pub enum ConfigAlgorithm {
    Pax(pax::PaxConfigAlgorithm),
    Cargo(cargo::CargoConfigAlgorithm),
}

impl Default for ConfigAlgorithm {
    fn default() -> Self {
        ConfigAlgorithm::Pax(pax::PaxConfigAlgorithm::Auto)
    }
}
