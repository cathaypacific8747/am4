//! Create *regular* scheduled routes. Checks for stopover availability and destination demand
//! to determine the best configuration.
use crate::aircraft::Aircraft;
use crate::airport::{db::Airports, Airport};
use crate::route::{
    config::ConfigAlgorithm,
    db::DemandMatrix,
    search::{ConcreteRoutes, Routes},
    Ci, Distance, DistanceError, FlightTime, FlightTimeError,
};
use crate::user::{GameMode, Settings};
use derive_more::Display;
use std::num::NonZeroU8;
use thiserror::Error;

#[derive(Debug, Clone, Error)]
pub enum RouteError<'a> {
    #[error("insufficient demand")]
    InsufficientDemand(&'a Airport),
}

#[derive(Debug, Clone, Error)]
pub enum ConfigError {
    #[error(transparent)]
    InvalidDistance(#[from] DistanceError),
    #[error(transparent)]
    InvalidFlightTime(#[from] FlightTimeError),
    #[error("minimum distance must be less than the maximum")]
    DistanceRangeOrdering,
    #[error("minimum flight time must be less than the maximum")]
    FlightTimeOrdering,
}

/// Collection of [ScheduledRoute], checked against the provided aircraft.
pub type ScheduledRoutes<'a> = Routes<'a, ScheduledRoute<'a>, ScheduleConfig<'a>>;

#[derive(Debug, Clone)]
pub struct ScheduledRoute<'a> {
    /// index into airports array
    destination: &'a Airport,
    direct_distance: Distance,
    stopover: Option<&'a Airport>,
    // ~~effective demand~~
    // configuration
    // income, fuel, co2, staff -> profit
}

#[derive(Debug, Clone)]
pub struct ScheduleConfig<'a> {
    airports: &'a Airports,
    origin: &'a Airport,
    aircraft: &'a Aircraft,
    game_mode: &'a GameMode,
    search_config: &'a SearchConfig<'a>, // TODO: rename
}

#[allow(unused)]
impl<'a> ConcreteRoutes<'a> {
    fn schedule(
        mut self,
        demand_matrix: &DemandMatrix,
        config: &SearchConfig,
    ) -> ScheduledRoutes<'a> {
        todo!()
    }
}

#[derive(Debug, Default)]
pub struct SearchConfig<'a> {
    user_settings: &'a Settings,
    constraint: Constraint,
    schedule: ScheduleStrategy,
    config: ConfigAlgorithm,
    ci: CiStrategy,
    sort_by: SortBy,
}

// NOTE: Irregular schedules (e.g. 7 trips in 48 hours) are not allowed.
// TODO: coerce floats?
/// Trips per day, the number of departures made within a 24 hour window,
/// starting from 02:00 UTC to the next day
type TripsPerDay = NonZeroU8;

/// Number of aircraft assigned to a single route.
type NumAircraft = NonZeroU8;

/// Attempt to maximise the [TripsPerDay] or strictly enforce a particular amount.
/// It is assumed that the departing conditions (e.g. marketing campaign) are identical.
#[derive(Debug, Clone, Display, Default)]
pub enum TripsPerDayStrategy {
    #[default]
    Maximise,
    Strict(TripsPerDay),
}

/// Attempt to maximise the [NumAircraft] or strictly enforce a particular amount.
/// It is assumed that each aircraft are identical (including any aircraft mods).
#[derive(Debug, Clone, Display)]
pub enum NumAircraftStrategy {
    Maximise,
    Strict(NumAircraft),
}

impl Default for NumAircraftStrategy {
    fn default() -> Self {
        Self::Strict(1.try_into().unwrap())
    }
}

/// A route schedule consists of the [TripsPerDay] and [NumAircraft], both of
/// which could be set to be maximised or strictly defined. In any case, trips
/// per day takes precendence over the number of aircraft
///
/// For example, if one chooses `3` trips per day and `Maximise` aircraft,
/// the algorithm will attempt to cram as many aircraft as possible to exhaust
/// the available daily demand.
#[derive(Debug, Clone)]
pub struct ScheduleStrategy {
    pub trips_per_day: TripsPerDayStrategy,
    pub num_aircraft: NumAircraftStrategy,
}

impl Default for ScheduleStrategy {
    /// Defaults to maximising the [TripsPerDay] on one aircraft.
    fn default() -> Self {
        Self {
            trips_per_day: TripsPerDayStrategy::Maximise,
            num_aircraft: NumAircraftStrategy::Strict(NonZeroU8::new(1).unwrap()),
        }
    }
}

#[derive(Debug, Clone)]
pub enum CiStrategy {
    Strict(Ci),
    AlignConstraint,
}

impl Default for CiStrategy {
    fn default() -> Self {
        Self::Strict(Ci::default())
    }
}

#[derive(Debug, Clone, Default)]
pub enum SortBy {
    #[default]
    ProfitPerAcPerDay,
    ProfitPerTrip,
}

#[derive(Debug, Clone, Default)]
pub enum Constraint {
    #[default]
    None,
    Distance(DistanceRange),
    FlightTime(FlightTimeRange),
}

#[derive(Debug, Clone)]
pub struct DistanceRange {
    min: Distance,
    max: Distance,
}

impl DistanceRange {
    fn new(min: Distance, max: Distance) -> Result<Self, ConfigError> {
        if min >= max {
            Err(ConfigError::DistanceRangeOrdering)
        } else {
            Ok(Self { min, max })
        }
    }
}

impl Default for DistanceRange {
    fn default() -> Self {
        Self {
            min: Distance::MIN,
            max: Distance::MAX,
        }
    }
}

#[derive(Debug, Clone)]
pub struct FlightTimeRange {
    min: FlightTime,
    max: FlightTime,
}

impl FlightTimeRange {
    fn new(min: FlightTime, max: FlightTime) -> Result<Self, ConfigError> {
        if min >= max {
            Err(ConfigError::FlightTimeOrdering)
        } else {
            Ok(Self { min, max })
        }
    }
}

impl Default for FlightTimeRange {
    fn default() -> Self {
        Self {
            min: FlightTime::MIN,
            max: FlightTime::MAX,
        }
    }
}
