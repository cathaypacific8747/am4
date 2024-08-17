//! Implements route filtering by maximum profit.
use crate::airport::Airport;
use crate::route::config::ConfigAlgorithm;
use crate::user::Settings;
use crate::utils::{Distance, FlightTime, RealError};
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
    #[error("invalid value: {0}")]
    InvalidDistanceOrFlightTime(#[from] RealError), // FIXME
    #[error("minimum distance must be less than the maximum")]
    DistanceRangeOrdering,
    #[error("minimum flight time must be less than the maximum")]
    FlightTimeOrdering,
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
#[derive(Debug, Clone, Display)]
pub enum TripsPerDayStrategy {
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

/// A route schedule consists of the [TripsPerDay] and [NumAircraft], both of
/// which could be set to be maximised or strictly defined. In any case, trips
/// per day takes precendence over the number of aircraft
///
/// For example, if one chooses `3` trips per day and `Maximise` aircraft,
/// the algorithm will attempt to cram as many aircraft as possible to exhaust
/// the available daily demand.
#[derive(Debug, Clone)]
pub struct Schedule {
    pub trips_per_day: TripsPerDayStrategy,
    pub num_aircraft: NumAircraftStrategy,
}

impl Default for Schedule {
    /// Defaults to maximising the [TripsPerDay] on one aircraft.
    fn default() -> Self {
        Self {
            trips_per_day: TripsPerDayStrategy::Maximise,
            num_aircraft: NumAircraftStrategy::Strict(NonZeroU8::new(1).unwrap()),
        }
    }
}

#[derive(Debug, Clone)]
pub enum SortBy {
    PerTrip,
    PerAircraftPerDay,
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
            min: Distance::MIN.try_into().unwrap(),
            max: Distance::CIRCUMFERENCE_EARTH.try_into().unwrap(),
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
            Err(ConfigError::DistanceRangeOrdering)
        } else {
            Ok(Self { min, max })
        }
    }
}

impl Default for FlightTimeRange {
    fn default() -> Self {
        Self {
            min: FlightTime::MIN.try_into().unwrap(),
            max: FlightTime::MAX.try_into().unwrap(),
        }
    }
}

#[derive(Debug, Clone)]
pub enum Constraint {
    Distance(DistanceRange),
    FlightTime(FlightTimeRange),
}

pub struct ProfitConfig<'a> {
    settings: &'a Settings,
    constraint: Option<Constraint>,
    trips_per_day: Schedule,
    config_algorithm: &'a ConfigAlgorithm,
    sort_by: SortBy,
}
