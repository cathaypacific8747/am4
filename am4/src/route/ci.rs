use derive_more::{Add, Display, Into};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ValidationError {
    #[error("ci must be less than or equal to 200")]
    Gt200,
}

/// Cost index, nondimensional
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Add, Into, Display)]
pub struct Ci(u8);

impl Ci {
    pub const MAX: Self = Self(200);
}

impl Default for Ci {
    fn default() -> Self {
        Self::MAX
    }
}

impl TryFrom<u8> for Ci {
    type Error = ValidationError;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        let value = Self(value);
        if value > Self::MAX {
            Err(Self::Error::Gt200)
        } else {
            Ok(value)
        }
    }
}
