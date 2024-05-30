pub mod cargo;
pub mod pax;

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
