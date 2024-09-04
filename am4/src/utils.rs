use std::{cmp::Ordering, collections::BinaryHeap, fmt::Debug};
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
pub enum FloatError {
    #[error("value must be greater than zero")]
    LeZero,
    #[error("value must be finite")]
    InfiniteOrNan,
}

pub trait RealValidator {
    fn validate_real(value: f32) -> Result<(), FloatError> {
        if value <= 0. {
            Err(FloatError::LeZero)
        } else if value.is_infinite() || value.is_nan() {
            Err(FloatError::InfiniteOrNan)
        } else {
            Ok(())
        }
    }
}
