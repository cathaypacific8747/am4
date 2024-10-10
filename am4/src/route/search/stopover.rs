use crate::{
    aircraft::Aircraft,
    airport::Airport,
    route::{db::DistanceMatrix, Distance},
};

use super::AbstractRoute;

#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct Stopover<'a>(&'a Airport);

impl<'a> From<&'a Airport> for Stopover<'a> {
    fn from(value: &'a Airport) -> Self {
        Self(value)
    }
}

impl<'a> Stopover<'a> {
    /// given an origin O, destination D, and range R, find the best intermediate stopover S,
    /// such that distance(O, S) + distance(S, D) is minimised, subject to distance < R.
    pub fn find_by_efficiency(
        airports: &'a [Airport],
        distances: &DistanceMatrix,
        origin: &Airport,
        destination: &Airport,
        aircraft: &Aircraft,
    ) -> Option<Self> {
        let mut best_stopover: Option<Self> = None;
        let mut best_dist_total = Distance::MAX;

        for candidate in airports.iter() {
            let Ok(inbound) = AbstractRoute::new(distances, origin, candidate) else {
                continue;
            };
            if !inbound.distance_valid(aircraft) {
                continue;
            }
            let Ok(outbound) = AbstractRoute::new(distances, destination, candidate) else {
                continue;
            };
            if !outbound.distance_valid(aircraft) {
                continue;
            }
            let dist_total = inbound.direct_distance + outbound.direct_distance;
            if dist_total < best_dist_total {
                best_stopover = Some(candidate.into());
                best_dist_total = dist_total;
            }
        }
        best_stopover
    }
}
