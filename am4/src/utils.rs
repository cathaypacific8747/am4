use derive_more::{Add, Display, Into};
use std::{cmp::Ordering, collections::BinaryHeap};
use thiserror::Error;

pub const MAX_SUGGESTIONS: usize = 5; // TODO: make this configurable

#[derive(Debug, Clone, PartialEq)]
pub struct Suggestion<T> {
    pub item: T,
    pub similarity: f64,
}

impl<T: PartialEq> Eq for Suggestion<T> {}

impl<T: PartialEq> Ord for Suggestion<T> {
    fn cmp(&self, other: &Self) -> Ordering {
        other.similarity.partial_cmp(&self.similarity).unwrap() // min heap
    }
}

impl<T: PartialEq> PartialOrd for Suggestion<T> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

pub fn queue_suggestions<'a, T: PartialEq>(
    heap: &mut BinaryHeap<Suggestion<&'a T>>,
    item: &'a T,
    similarity: f64,
) {
    if heap.len() < MAX_SUGGESTIONS {
        heap.push(Suggestion { item, similarity });
    } else if similarity > heap.peek().unwrap().similarity {
        heap.pop();
        heap.push(Suggestion { item, similarity });
    }
}

#[derive(Debug, Error)]
pub enum ParseError {
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Archive error: {0}")]
    ArchiveError(String),
    #[error("Deserialise error: {0}")]
    DeserialiseError(String),
    #[error("Serialise error: {0}")]
    SerialiseError(String),
    #[error("Invalid data length: expected {expected} routes, got {actual}")]
    InvalidDataLength { expected: usize, actual: usize },
}

#[derive(Debug, Clone, Error)]
pub enum RealError {
    #[error("value must be greater than zero")]
    LeZero,
    #[error("value must be finite")]
    InfiniteOrNan,
}

pub trait Real {
    fn validate_normal(value: f32) -> Result<(), RealError> {
        if value <= 0. {
            Err(RealError::LeZero)
        } else if value.is_infinite() || value.is_nan() {
            Err(RealError::InfiniteOrNan)
        } else {
            Ok(())
        }
    }
}

/// Distance in kilometers
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Add, Into, Display)]
pub struct Distance(f32);

impl Distance {
    pub const MIN: f32 = 100f32;
    pub const RADIUS_EARTH: f32 = 6371f32;
    pub const CIRCUMFERENCE_EARTH: f32 = 2f32 * std::f32::consts::PI * Self::RADIUS_EARTH;
}

impl Real for Distance {}

impl TryFrom<f32> for Distance {
    type Error = RealError;

    fn try_from(value: f32) -> Result<Self, Self::Error> {
        Self::validate_normal(value)?;
        Ok(Distance(value))
    }
}

/// Flight time in hours
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Add, Into, Display)]
pub struct FlightTime(f32);

impl FlightTime {
    pub const MIN: f32 = 0.1f32;
    pub const MAX: f32 = 72f32;
}

impl Real for FlightTime {}

impl TryFrom<f32> for FlightTime {
    type Error = RealError;

    fn try_from(value: f32) -> Result<Self, Self::Error> {
        Self::validate_normal(value)?;
        Ok(FlightTime(value))
    }
}
