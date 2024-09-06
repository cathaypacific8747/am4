use crate::utils::{PositiveReal, PositiveRealError};
use derive_more::{Add, Display, Into};
use std::num::ParseFloatError;
use thiserror::Error;

#[derive(Debug, Clone, Error)]
pub enum FlightTimeError {
    #[error("not a valid float: {0}")]
    ParseError(#[source] ParseFloatError),
    #[error(transparent)]
    FloatError(#[from] PositiveRealError),
}

/// Flight time, hrs
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Add, Into, Display)]
pub struct FlightTime(f32);

impl FlightTime {
    pub const MIN: Self = Self(0.1);
    pub const MAX: Self = Self(72.);

    pub fn new_unchecked(value: f32) -> Self {
        Self(value)
    }

    pub fn get(&self) -> f32 {
        self.0
    }
}

impl PositiveReal for FlightTime {}

impl TryFrom<f32> for FlightTime {
    type Error = PositiveRealError;

    fn try_from(value: f32) -> Result<Self, Self::Error> {
        Self::validate_positive_real(value)?;
        Ok(Self(value))
    }
}
