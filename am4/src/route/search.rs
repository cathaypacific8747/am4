use crate::config::ConfigAlgorithm;

impl AircraftRouteOptions {
    pub fn new(
        tpd_mode: TPDMode,
        trips_per_day_per_ac: u16,
        max_distance: f64,
        max_flight_time: f32,
        config_algorithm: ConfigAlgorithm,
        sort_by: SortBy,
    ) -> Self {
        Self {
            tpd_mode,
            trips_per_day_per_ac,
            max_distance,
            max_flight_time,
            config_algorithm,
            sort_by,
        }
    }
}

pub struct AircraftRouteOptions {
    pub tpd_mode: TPDMode,
    pub trips_per_day_per_ac: u16,
    pub max_distance: f64,
    pub max_flight_time: f32,
    pub config_algorithm: ConfigAlgorithm,
    pub sort_by: SortBy,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TPDMode {
    Auto,
    StrictAllowMultipleAc,
    Strict,
}

impl Default for TPDMode {
    fn default() -> Self {
        TPDMode::Auto
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SortBy {
    PerTrip,
    PerAcPerDay,
}

impl Default for SortBy {
    fn default() -> Self {
        SortBy::PerTrip
    }
}
