use crate::airport::Point;
use crate::utils::{PositiveReal, PositiveRealError};
use derive_more::{Add, Display, Into};
use std::num::ParseFloatError;
use std::str::FromStr;
use thiserror::Error;

#[cfg(feature = "rkyv")]
use rkyv::{Archive as Ra, Deserialize as Rd, Serialize as Rs};
#[cfg(feature = "serde")]
use serde::Deserialize;

#[derive(Debug, Clone, Error)]
pub enum DistanceError {
    #[error("not a valid float: {0}")]
    ParseError(#[source] ParseFloatError),
    #[error(transparent)]
    FloatError(#[from] PositiveRealError),
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

    pub fn new_unchecked(value: f32) -> Self {
        Self(value)
    }

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

impl PositiveReal for Distance {}

impl TryFrom<f32> for Distance {
    type Error = PositiveRealError;

    fn try_from(value: f32) -> Result<Self, Self::Error> {
        Self::validate_positive_real(value)?;
        Ok(Self(value))
    }
}

impl FromStr for Distance {
    type Err = DistanceError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let value = s.parse::<f32>().map_err(DistanceError::ParseError)?;
        Ok(Distance::try_from(value)?)
    }
}

#[test]
fn parse_distance() {
    let v = "13e3".parse::<Distance>().unwrap();
    assert_eq!(v.get(), 13000.0);

    assert!("-1".parse::<Distance>().is_err());
    assert!("inf".parse::<Distance>().is_err());
    assert!("NaN".parse::<Distance>().is_err());
}

#[test]
fn parse_distance_range() {
    use crate::utils::{Filter, FilterError};

    type F = Filter<Distance>;
    type FE = FilterError<DistanceError>;

    assert!(
        matches!("13..13000".parse::<F>().unwrap(), F::Range(v) if v == ((Distance::new_unchecked(13f32))..(Distance::new_unchecked(13000f32))))
    );
    assert!("..NaN"
        .parse::<F>()
        .is_err_and(|e| matches!(e, FE::InvalidBound(_))));
    assert!("NaN"
        .parse::<F>()
        .is_err_and(|e| matches!(e, FE::InvalidUpperBound(_))));
}
