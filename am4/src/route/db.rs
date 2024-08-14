use crate::airport::{db::AIRPORT_COUNT, Airport};
use crate::route::demand::pax::PaxDemand;
use crate::utils::ParseError;
use core::ops::Index;
use rkyv::{self, AlignedVec, Deserialize};

pub const ROUTE_COUNT: usize = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;

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

impl Index<(usize, usize)> for Demands {
    type Output = PaxDemand;

    /// SAFETY: will panic if oidx == didx.
    fn index(&self, (oidx, didx): (usize, usize)) -> &Self::Output {
        let idx = if oidx > didx {
            ((didx * (2 * AIRPORT_COUNT - didx - 1)) >> 1) + oidx - didx - 1
        } else {
            ((oidx * (2 * AIRPORT_COUNT - oidx - 1)) >> 1) + didx - oidx - 1
        };
        self.0.index(idx)
    }
}

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
