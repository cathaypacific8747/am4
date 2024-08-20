/*!
Implements an in-memory, pax demand database.
*/

use crate::airport::{db::AIRPORT_COUNT, Airport};
use crate::route::demand::PaxDemand;
use crate::utils::ParseError;
use core::ops::Index;
use rkyv::{self, AlignedVec, Deserialize};

pub const ROUTE_COUNT: usize = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;

/// A route constructed from one [Airport] to the other is associated
/// with an **undirected** pair of (economy, business, first) class demands.
///
/// We represent it as a flattened version of the upper triangular matrix.
/// For example, consider a world with 4 airports, the index into the [Vec] would be:
///
/// ```txt
///     0  1  2  3  <-- origin index
///    ___________
/// 0 | ·  0  1  2
/// 1 | 0  ·  3  4
/// 2 | 1  3  ·  5
/// 3 | 2  4  5  ·
///
/// ^
/// └-- destination index
/// ```
///
/// Excluding routes with origin equal to the destination, we have
/// `n * (n - 1) / 2 = 7630371` possible routes, where `n = 3907` is the [AIRPORT_COUNT].
#[derive(Debug)]
pub struct Demands(Vec<PaxDemand>);

impl Demands {
    pub fn from_bytes(buffer: &[u8]) -> Result<Self, ParseError> {
        // ensure serialised bytes can be deserialised
        let archived = rkyv::check_archived_root::<Vec<PaxDemand>>(buffer)
            .map_err(|e| ParseError::ArchiveError(e.to_string()))?;

        let demands: Vec<PaxDemand> = archived
            .deserialize(&mut rkyv::Infallible)
            .map_err(|e| ParseError::DeserialiseError(e.to_string()))?;

        if demands.len() != ROUTE_COUNT {
            return Err(ParseError::InvalidDataLength {
                expected: ROUTE_COUNT,
                actual: demands.len(),
            });
        }

        Ok(Demands(demands))
    }

    pub fn data(&self) -> &Vec<PaxDemand> {
        &self.0
    }
}

/// SAFETY: panics when both are 0 (underflow)
fn index(oidx: usize, didx: usize) -> usize {
    let (x, y) = if oidx > didx {
        (didx, oidx)
    } else {
        (oidx, didx)
    };
    x * (2 * AIRPORT_COUNT - y - 1) / 2 + (y - x - 1)
}

impl Index<(usize, usize)> for Demands {
    type Output = PaxDemand;

    /// SAFETY: panics when both are 0 (underflow)
    fn index(&self, (oidx, didx): (usize, usize)) -> &Self::Output {
        &self.0[index(oidx, didx)]
    }
}

// TODO: remove distance matrix.

#[derive(Debug)]
pub struct Distances(Vec<f32>);

impl Distances {
    /// Load the distance matrix from a rkyv serialised buffer
    pub fn from_bytes(buffer: &[u8]) -> Result<Self, ParseError> {
        let archived = rkyv::check_archived_root::<Vec<f32>>(buffer)
            .map_err(|e| ParseError::ArchiveError(e.to_string()))?;

        let distances: Vec<f32> = archived
            .deserialize(&mut rkyv::Infallible)
            .map_err(|e| ParseError::DeserialiseError(e.to_string()))?;

        if distances.len() != ROUTE_COUNT {
            return Err(ParseError::InvalidDataLength {
                expected: ROUTE_COUNT,
                actual: distances.len(),
            });
        }

        Ok(Distances(distances))
    }

    /// Compute the distance matrix with haversine
    pub fn from_airports(aps: &[Airport]) -> Self {
        assert!(aps.len() == AIRPORT_COUNT); // compiler optimisation
        let mut d = Vec::<f32>::with_capacity(ROUTE_COUNT);
        let mut x: usize = 0;
        let mut y: usize = 0;
        for _ in 0..ROUTE_COUNT {
            y += 1;
            if y == AIRPORT_COUNT {
                x += 1;
                y = x + 1;
            }
            d.push(aps[x].distance_to(&aps[y]));
        }
        assert_eq!(d.len(), ROUTE_COUNT);
        Distances(d)
    }

    pub fn to_bytes(&self) -> Result<AlignedVec, ParseError> {
        let av = rkyv::to_bytes::<Vec<f32>, 30_521_492>(&self.0)
            .map_err(|e| ParseError::SerialiseError(e.to_string()))?;
        Ok(av)
    }

    pub fn data(&self) -> &Vec<f32> {
        &self.0
    }
}
