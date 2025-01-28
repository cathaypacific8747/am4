/*!
 * Implements utilities for searching optimal destinations from an origin [Airport].
 *
 * We adopt a layered, modular approach to "eliminate" candidates for each rule.
 * This allows us to branch off any layer and perform multiple queries.
 *
 * ```txt
 * origin
 *   |
 *   +--- (direct distance) --- destination
 *   |
 *   v
 * AbstractRoute
 *   |
 *   +--- aircraft
 *   +--- user game mode
 *   |
 *   filter: range  --> too short
 *   filter: runway --> too short
 *   |
 * ConcreteRoute ------------> Sell airport optimisation
 *   |                |------> Contribution optimisation
 *   |
 *   +--- user settings
 *   +--- demand
 *   |
 *   filter: demand --> too low
 *   filter(toggleable): stopover finding --> no stopover
 *   |                         |
 *   +---- stopover -----------|
 *   +---- configuration
 *   |
 * ScheduledRoute
 * ```
 */

pub mod schedule;
pub mod stopover;

// TODO: const generic to silently ignore errors
use crate::airport::{db::Airports, Airport};
use crate::route::db::DistanceMatrix;
use crate::route::Distance;
use thiserror::Error;

use crate::aircraft::Aircraft;
use crate::user::GameMode;

/// Returns when a route returns to itself or is <= 100km
#[derive(Debug, Clone, Error)]
#[error("distance is too short, must be greater than 100km")]
pub struct DistanceTooShort;

#[derive(Debug, Clone, Error)]
pub enum RouteError {
    #[error(transparent)]
    DistanceTooShort(#[from] DistanceTooShort),
    #[error("distance is above the aircraft's maximum range")]
    DistanceAboveRange,
    #[error("runway length is too short")]
    RunwayTooShort,
    #[error(transparent)]
    ScheduleError(#[from] schedule::ScheduleError),
}

#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct FailedRoute<'a> {
    destination: &'a Airport,
    error: RouteError,
}

// NOTE: not using struct of arrays for now. keeping it simple
/// A generic routelist, holding destinations from a given origin.
/// For performance, details ([Routes::routes]) are kept as minimal as possible
/// unless the user explicitly requests more.
#[derive(Debug, Clone)]
pub struct Routes<'a, R, C> {
    routes: Vec<R>,
    errors: Vec<FailedRoute<'a>>,
    config: C,
}

impl<R, C> Routes<'_, R, C> {
    /// Get the list of routes (e.g. [AbstractRoutes], [ConcreteRoutes])
    pub fn routes(&self) -> &[R] {
        &self.routes
    }

    /// Get details about routing failures (e.g. insufficient range, runway too short etc.)
    pub fn errors(&self) -> &[FailedRoute] {
        &self.errors
    }

    /// Get the metadata (e.g. [AbstractConfig], [ConcreteConfig])
    pub fn config(&self) -> &C {
        &self.config
    }
}

pub type AbstractRoutes<'a> = Routes<'a, AbstractRoute<'a>, AbstractConfig<'a>>;

#[derive(Debug, Clone)]
pub struct AbstractRoute<'a> {
    /// index into airports array
    destination: &'a Airport,
    direct_distance: Distance,
}

impl<'a> AbstractRoute<'a> {
    /// Create a direct [AbstractRoute] from the origin to the destination.
    fn new(
        distances: &DistanceMatrix,
        origin: &Airport,
        destination: &'a Airport,
    ) -> Result<Self, DistanceTooShort> {
        if destination.idx == origin.idx {
            return Err(DistanceTooShort);
        }
        let direct_distance = distances[(origin.idx, destination.idx)];
        if direct_distance < Distance::MIN {
            return Err(DistanceTooShort);
        }
        Ok(Self {
            destination,
            direct_distance,
        })
    }

    fn runway_valid(&self, aircraft: &Aircraft, game_mode: &GameMode) -> bool {
        match game_mode {
            GameMode::Easy => true,
            GameMode::Realism => self.destination.rwy >= aircraft.rwy,
        }
    }

    fn distance_valid(&self, aircraft: &Aircraft) -> bool {
        self.direct_distance.get() < aircraft.range as f32 * 2.0
    }
}

#[derive(Debug, Clone)]
pub struct AbstractConfig<'a> {
    airports: &'a Airports,
    origin: &'a Airport,
}

impl<'a> AbstractRoutes<'a> {
    /// Create an abstract routelist from an origin airport
    /// to multiple destination airports.
    pub fn new(
        airports: &'a Airports,
        distances: &'a DistanceMatrix,
        origin: &'a Airport,
        destinations: &'a [Airport],
    ) -> Self {
        let mut routes = Vec::new();
        let mut errors = Vec::new();
        for destination in destinations {
            match AbstractRoute::new(distances, origin, destination) {
                Ok(route) => routes.push(route),
                Err(e) => errors.push(FailedRoute {
                    destination,
                    error: e.into(),
                }),
            }
        }
        Self {
            routes,
            errors,
            config: AbstractConfig { airports, origin },
        }
    }

    /// Consumes and prunes the abstract route list that
    /// do not meet the aircraft's range and runway constraints,
    pub fn with_aircraft(
        mut self,
        aircraft: &'a Aircraft,
        game_mode: &'a GameMode,
    ) -> ConcreteRoutes<'a> {
        self.routes.retain(|route| {
            if !route.distance_valid(aircraft) {
                self.errors.push(FailedRoute {
                    destination: route.destination,
                    error: RouteError::DistanceAboveRange,
                });
                return false;
            }
            if !route.runway_valid(aircraft, game_mode) {
                self.errors.push(FailedRoute {
                    destination: route.destination,
                    error: RouteError::RunwayTooShort,
                });
                return false;
            }
            true
        });
        ConcreteRoutes {
            routes: self.routes,
            errors: self.errors,
            config: ConcreteConfig {
                airports: self.config.airports,
                origin: self.config.origin,
                aircraft,
                game_mode,
            },
        }
    }
}

/// Collection of [AbstractRoutes], checked against the provided aircraft.
pub type ConcreteRoutes<'a> = Routes<'a, AbstractRoute<'a>, ConcreteConfig<'a>>;

#[derive(Debug, Clone)]
pub struct ConcreteConfig<'a> {
    airports: &'a Airports,
    origin: &'a Airport,
    aircraft: &'a Aircraft,
    game_mode: &'a GameMode,
}
