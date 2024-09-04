use crate::utils::{FloatError, RealValidator};
use derive_more::{Add, Display, Into};
use thiserror::Error;

#[derive(Debug, Clone, Error)]
pub enum ValidationError {
    #[error(transparent)]
    FloatError(#[from] FloatError),
}

/// Flight time, hrs
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Add, Into, Display)]
pub struct FlightTime(f32);

impl FlightTime {
    pub const MIN: Self = Self(0.1);
    pub const MAX: Self = Self(72.);

    pub fn get(&self) -> f32 {
        self.0
    }
}

impl RealValidator for FlightTime {}

impl TryFrom<f32> for FlightTime {
    type Error = FloatError;

    fn try_from(value: f32) -> Result<Self, Self::Error> {
        Self::validate_real(value)?;
        Ok(Self(value))
    }
}
