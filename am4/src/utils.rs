use std::ops::{Range, RangeFrom, RangeTo};
use std::str::FromStr;
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

/// For rkyv archives
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
pub enum PositiveRealError {
    #[error("value must be greater than zero")]
    LeZero,
    #[error("value must be finite")]
    InfiniteOrNan,
}

pub trait PositiveReal {
    fn validate_positive_real(value: f32) -> Result<(), PositiveRealError> {
        if value <= 0. {
            Err(PositiveRealError::LeZero)
        } else if value.is_infinite() || value.is_nan() {
            Err(PositiveRealError::InfiniteOrNan)
        } else {
            Ok(())
        }
    }
}

// TODO: relax float
#[derive(Debug, Clone, Error)]
pub enum FilterError<E> {
    #[error("empty bounds")]
    EmptyBounds,
    /// e.g. `ABC`
    #[error("not a range, failed to parse as lone value")]
    InvalidUpperBound(E),
    /// e.g. `..NaN`
    #[error("failed to parse one of the bounds")]
    InvalidBound(#[from] E),
    #[error("lower bound must be less than the upper bound")]
    LowerBoundGeUpperBound,
}

/// A range that can be unbounded, [half-bounded][Range],
/// [bounded inclusively below][RangeFrom] or [bounded exclusively][RangeTo]
/// above a certain value.
#[derive(Debug, Clone, Default)]
pub enum Filter<T> {
    #[default]
    RangeFull,
    Range(Range<T>),
    RangeFrom(RangeFrom<T>),
    RangeTo(RangeTo<T>),
}

impl<T, E> FromStr for Filter<T>
where
    T: PartialEq + PartialOrd + FromStr<Err = E>,
{
    type Err = FilterError<E>;

    /// Parse `Option<T>..Option<T>`, validating `T` with [FromStr].
    /// If no `..` is provided (lone value), it defaults to the an upper bound
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.split_once("..") {
            Some(("", "")) => Err(FilterError::EmptyBounds),
            Some(("", upper)) => Ok(Self::RangeTo(..(upper.parse::<T>()?))),
            Some((lower, "")) => Ok(Self::RangeFrom((lower.parse::<T>()?)..)),
            Some((lower, upper)) => {
                let (lower, upper) = (lower.parse::<T>()?, upper.parse::<T>()?);
                if lower >= upper {
                    return Err(FilterError::LowerBoundGeUpperBound);
                }
                Ok(Self::Range(lower..upper))
            }
            None => match s.parse::<T>() {
                Ok(upper) => Ok(Self::RangeTo(..upper)),
                Err(e) => Err(Self::Err::InvalidUpperBound(e)),
            },
        }
    }
}

impl<T: PartialOrd> Filter<T> {
    pub fn contains(&self, value: &T) -> bool {
        match self {
            Self::Range(r) => r.contains(value),
            Self::RangeFrom(r) => r.contains(value),
            Self::RangeTo(r) => r.contains(value),
            Self::RangeFull => true,
        }
    }
}

#[test]
fn parse_distance_range() {
    use std::num::ParseFloatError;

    type F = Filter<f32>;
    type FE = FilterError<ParseFloatError>;

    assert!(matches!("13..13000".parse::<F>().unwrap(), F::Range(r) if r == (13f32..13000f32)));
    assert!(matches!("..13000".parse::<F>().unwrap(), F::RangeTo(r) if r == (..13000f32)));
    assert!(matches!("13000".parse::<F>().unwrap(), F::RangeTo(r) if r == (..13000f32)));
    assert!(matches!("13..".parse::<F>().unwrap(), F::RangeFrom(r) if r == (13f32..)));
    // not handling 13... -> (13.0)..
    assert!(matches!("...13".parse::<F>().unwrap(), F::RangeTo(r) if r == (..0.13f32)));
    assert!(matches!(
        "13e-13..13E13".parse::<F>().unwrap(),
        F::Range(r) if r == (13e-13f32..13e13f32)
    ));

    assert!(".."
        .parse::<F>()
        .is_err_and(|e| matches!(e, FE::EmptyBounds)));
    assert!("AAAAAAAA"
        .parse::<F>()
        .is_err_and(|e| matches!(e, FE::InvalidUpperBound(_))));
    assert!("..AAAAAAAA"
        .parse::<F>()
        .is_err_and(|e| matches!(e, FE::InvalidBound(_))));
    assert!("31..13"
        .parse::<F>()
        .is_err_and(|e| matches!(e, FE::LowerBoundGeUpperBound)));
    assert!("0..0"
        .parse::<F>()
        .is_err_and(|e| matches!(e, FE::LowerBoundGeUpperBound)));
}
