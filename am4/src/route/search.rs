/*!
```txt
origin
  |
  +--- (direct distance) --- destination
  |
  v
AbstractRoute
  |
  +--- aircraft
  |
  filter: range  --> too short
  filter: runway --> too short
  |
  |
  +--- user settings
  +--- demand
  |
  filter: demand --> too low
  filter(toggleable): stopover finding --> no stopover
  |                         |
  +---- stopover -----------|
  |
  v
Route
  |--- configuration optimisation
  |
Itinerary
```
*/

use crate::airport::{db::Airports, Airport, Id};
use crate::route::db::Demands;
use thiserror::Error;

use super::demand::pax::PaxDemand;

#[derive(Debug, Error)]
pub enum RouteError {
    #[error("Airport `{0:?}` not found in the database.")]
    AirportNotFound(Id),
    #[error("Cannot create a self-referential route for airport `{0:?}`.")]
    SelfReferential(Id),
}

/// A valid airport that is guaranteed to exist in the demand table.
#[derive(Debug)]
pub struct CheckedAirport<'a> {
    airport: &'a Airport,
    /// Used to index into [Demands].
    idx: usize,
}

impl<'a> CheckedAirport<'a> {
    pub fn new(airports: &Airports, airport: &'a Airport) -> Result<Self, RouteError> {
        let idx = airports
            .index()
            .get(&(airport.id.clone().into()))
            .ok_or(RouteError::AirportNotFound(airport.id.clone()))
            .copied()?;
        Ok(Self { airport, idx })
    }
}

#[derive(Debug)]
pub struct RouteSearch<'a> {
    airports: &'a Airports,
    demands: &'a Demands,
    origin: CheckedAirport<'a>,
}

impl<'a> RouteSearch<'a> {
    pub fn new(
        airports: &'a Airports,
        demands: &'a Demands,
        origin: &'a Airport,
    ) -> Result<Self, RouteError> {
        let origin = CheckedAirport::new(&airports, &origin)?;
        Ok(Self {
            airports,
            demands,
            origin,
        })
    }

    pub fn create_abstract(
        &self,
        destinations: &'a [Airport],
    ) -> Vec<Result<AbstractRoute<'a>, RouteError>> {
        destinations
            .into_iter()
            .map(|airport| {
                if airport.id == self.origin.airport.id {
                    Err(RouteError::SelfReferential(airport.id.clone()))
                } else {
                    let destination = CheckedAirport::new(&self.airports, airport)?;
                    let demand = self.demands[(self.origin.idx, destination.idx)].clone(); // owned
                    Ok(AbstractRoute {
                        destination,
                        demand,
                    })
                }
            })
            .collect()
    }
}

#[derive(Debug)]
pub struct AbstractRoute<'a> {
    /// index into airports array
    pub destination: CheckedAirport<'a>,
    pub demand: PaxDemand,
}
