//! Implements greedy configuration algorithms for pax and cargo aircraft

mod cargo;
mod pax;

pub use cargo::{CargoConfig, CargoConfigAlgorithm};
pub use pax::{PaxConfig, PaxConfigAlgorithm};

#[derive(Debug, Default)]
pub enum ConfigAlgorithm {
    #[default]
    Auto,
    Pax(pax::PaxConfigAlgorithm),
    Cargo(cargo::CargoConfigAlgorithm),
}

// TODO: redirect auto to pax and cargo respectively
