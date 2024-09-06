//! Create *regular* scheduled routes. Checks for stopover availability and destination demand
//! to determine the best configuration.
use crate::aircraft::Aircraft;
use crate::airport::{db::Airports, Airport};
use crate::route::{
    config::ConfigAlgorithm,
    db::DemandMatrix,
    search::{ConcreteRoutes, Routes},
    Ci, Distance, DistanceError, FlightTimeError,
};
use crate::user::{GameMode, Settings};
use crate::utils::{Filter, FilterError};
use derive_more::Display;
use std::num::NonZeroU8;
use thiserror::Error;

#[derive(Debug, Clone, Error)]
pub enum ScheduleError<'a> {
    #[error("distance to `{0:?}` ({1:2} km) failed the constraint")]
    DistanceConstraint(&'a Airport, Distance),
    #[error("insufficient demand")]
    InsufficientDemand(&'a Airport),
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
    pub fn schedule(
        mut self,
        demand_matrix: &'a DemandMatrix,
        search_config: &'a SearchConfig,
    ) -> ScheduledRoutes<'a> {
        let routes: Vec<_> = self
            .routes
            .iter()
            .filter_map(|route| {
                if !search_config
                    .distance_filter
                    .contains(&route.direct_distance)
                {
                    self.errors.push(
                        ScheduleError::DistanceConstraint(route.destination, route.direct_distance)
                            .into(),
                    );
                    return None;
                }
                Some(ScheduledRoute {
                    destination: route.destination,
                    direct_distance: route.direct_distance,
                    stopover: None,
                })
            })
            .collect();
        ScheduledRoutes {
            routes,
            errors: self.errors,
            config: ScheduleConfig {
                airports: self.config.airports,
                origin: self.config.origin,
                aircraft: self.config.aircraft,
                game_mode: self.config.game_mode,
                search_config,
            },
        }
    }
}

#[derive(Debug, Clone, Error)]
pub enum SearchConfigError {
    #[error("filter error: {0}")]
    DistanceFilterError(FilterError<DistanceError>),
    #[error("filter error: {0}")]
    FlightTimeFilterError(FilterError<FlightTimeError>),
}

#[derive(Debug, Default)]
pub struct SearchConfig<'a> {
    pub user_settings: &'a Settings,
    pub distance_filter: Filter<Distance>,
    pub schedule: ScheduleStrategy,
    pub config: ConfigAlgorithm,
    pub ci: CiStrategy,
    pub sort_by: SortBy,
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
