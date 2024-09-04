/*!
Implements an in-memory, pax demand and distance database.

A route constructed from one [Airport] to the other is associated
with an **undirected** pair of:
- (economy, business, first) class demands
- direct distance

We represent it as a flattened version of the
[strictly upper triangular matrix][StrictlyUpperTriangularMatrix].

Excluding routes with origin equal to the destination, there are
`n * (n - 1) / 2 = 7630371` possible routes, where `n = 3907` is the [AIRPORT_COUNT].
*/

use crate::airport::{db::AIRPORT_COUNT, Airport};
use crate::route::{demand::PaxDemand, Distance};
use crate::utils::ParseError;
use core::ops::Index;

#[cfg(feature = "rkyv")]
use rkyv::{self, AlignedVec, Deserialize};

pub const ROUTE_COUNT: usize = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;

/// A flattened version of the strictly upper triangular matrix.
///
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
// TODO: using row and column for convenience for now, switch to index
#[derive(Debug)]
pub struct StrictlyUpperTriangularMatrix<const N: usize> {
    curr: usize,
    /// Row number
    i: usize,
    /// Column number
    j: usize,
}

impl<const N: usize> StrictlyUpperTriangularMatrix<N> {
    const CURR_MAX: usize = N * (N - 1) / 2;

    /// Compute the index of the flattened [Vec] representation,
    /// given the row and column number.
    ///
    /// Panics if `i >= j` (underflow).
    pub fn index((i, j): (usize, usize)) -> usize {
        i * (2 * N - i - 1) / 2 + (j - i - 1)
    }
}

impl<const N: usize> Default for StrictlyUpperTriangularMatrix<N> {
    fn default() -> Self {
        Self {
            curr: 0,
            i: 0,
            j: 0,
        }
    }
}

impl<const N: usize> Iterator for StrictlyUpperTriangularMatrix<N> {
    type Item = (usize, usize);

    fn next(&mut self) -> Option<Self::Item> {
        if self.curr >= Self::CURR_MAX {
            return None;
        }
        self.j += 1;
        if self.j == N {
            self.i += 1;
            self.j = self.i + 1;
        }
        self.curr += 1;
        Some((self.i, self.j))
    }
}

/// Panics if `oidx == didx` (underflow)
fn get_index(oidx: usize, didx: usize) -> usize {
    let (i, j) = if oidx > didx {
        (didx, oidx)
    } else {
        (oidx, didx)
    };
    StrictlyUpperTriangularMatrix::<AIRPORT_COUNT>::index((i, j))
}

#[derive(Debug)]
pub struct DemandMatrix(Vec<PaxDemand>);

impl DemandMatrix {
    #[cfg(feature = "rkyv")]
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

        Ok(DemandMatrix(demands))
    }

    pub fn data(&self) -> &Vec<PaxDemand> {
        &self.0
    }
}

impl Index<(usize, usize)> for DemandMatrix {
    type Output = PaxDemand;

    /// Panics if `oidx == didx` (underflow)
    fn index(&self, (oidx, didx): (usize, usize)) -> &Self::Output {
        &self.0[get_index(oidx, didx)]
    }
}

#[derive(Debug)]
pub struct DistanceMatrix(Vec<Distance>);

impl DistanceMatrix {
    /// Load the distance matrix from a rkyv serialised buffer
    #[cfg(feature = "rkyv")]
    pub fn from_bytes(buffer: &[u8]) -> Result<Self, ParseError> {
        let archived = rkyv::check_archived_root::<Vec<Distance>>(buffer)
            .map_err(|e| ParseError::ArchiveError(e.to_string()))?;

        let distances: Vec<_> = archived
            .deserialize(&mut rkyv::Infallible)
            .map_err(|e| ParseError::DeserialiseError(e.to_string()))?;

        if distances.len() != ROUTE_COUNT {
            return Err(ParseError::InvalidDataLength {
                expected: ROUTE_COUNT,
                actual: distances.len(),
            });
        }

        Ok(DistanceMatrix(distances))
    }

    /// Compute the distance matrix with haversine
    pub fn from_airports(aps: &[Airport]) -> Self {
        let d: Vec<_> = StrictlyUpperTriangularMatrix::<AIRPORT_COUNT>::default()
            .map(|(i, j)| Distance::haversine(&aps[i].location, &aps[j].location))
            .collect();
        debug_assert_eq!(d.len(), ROUTE_COUNT);
        Self(d)
    }

    #[cfg(feature = "rkyv")]
    pub fn to_bytes(&self) -> Result<AlignedVec, ParseError> {
        let av = rkyv::to_bytes::<Vec<_>, 30_521_492>(&self.0)
            .map_err(|e| ParseError::SerialiseError(e.to_string()))?;
        Ok(av)
    }

    pub fn data(&self) -> &Vec<Distance> {
        &self.0
    }
}

impl Index<(usize, usize)> for DistanceMatrix {
    type Output = Distance;

    /// Panics if `oidx == didx` (underflow)
    fn index(&self, (oidx, didx): (usize, usize)) -> &Self::Output {
        &self.0[get_index(oidx, didx)]
    }
}
