use crate::airport::Point;
use crate::utils::{FloatError, RealValidator};
use derive_more::{Add, Display, Into};
use thiserror::Error;

#[cfg(feature = "rkyv")]
use rkyv::{Archive as Ra, Deserialize as Rd, Serialize as Rs};
#[cfg(feature = "serde")]
use serde::Deserialize;

#[derive(Debug, Clone, Error)]
pub enum ValidationError {
    #[error(transparent)]
    FloatError(#[from] FloatError),
}

/// Distance, km
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Add, Into, Display)]
#[cfg_attr(feature = "rkyv", derive(Ra, Rd, Rs), archive(check_bytes))]
#[cfg_attr(feature = "serde", derive(Deserialize))]
pub struct Distance(f32);

impl Distance {
    pub const MIN: Self = Self(100.);
    pub const MAX: Self = Self(4. * std::f32::consts::PI * Self::RADIUS_EARTH); // 2 * circumference

    const RADIUS_EARTH: f32 = 6371.;

    #[inline]
    pub fn haversine(origin: &Point, destination: &Point) -> Self {
        let lat1 = origin.lat.to_radians();
        let lon1 = origin.lng.to_radians();

        let lat2 = destination.lat.to_radians();
        let lon2 = destination.lng.to_radians();

        let dlat = lat2 - lat1;
        let dlon = lon2 - lon1;

        let a = (dlat / 2.0).sin().powi(2) + lat1.cos() * lat2.cos() * (dlon / 2.0).sin().powi(2);
        let c = 2.0 * a.sqrt().asin();

        Self(Self::RADIUS_EARTH * c)
    }

    pub fn get(&self) -> f32 {
        self.0
    }
}

impl RealValidator for Distance {}

impl TryFrom<f32> for Distance {
    type Error = FloatError;

    fn try_from(value: f32) -> Result<Self, Self::Error> {
        Self::validate_real(value)?;
        Ok(Self(value))
    }
}
