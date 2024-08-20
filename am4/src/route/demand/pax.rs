use derive_more::Display;

#[cfg(feature = "rkyv")]
use rkyv::{Archive as Ra, Deserialize as Rd, Serialize as Rs};
#[cfg(feature = "serde")]
use serde::Deserialize;

#[derive(Debug, Clone, PartialEq, Display)]
#[display("Y{y} J{j} F{f}")]
#[cfg_attr(feature = "serde", derive(Deserialize))]
#[cfg_attr(feature = "rkyv", derive(Ra, Rd, Rs), archive(check_bytes))]
pub struct PaxDemand {
    pub y: u16,
    pub j: u16,
    pub f: u16,
}

impl PaxDemand {
    pub fn equivalent(&self) -> u16 {
        self.y + 2 * self.j + 3 * self.f
    }
}

impl std::ops::Div<f64> for PaxDemand {
    type Output = Self;

    fn div(self, rhs: f64) -> Self::Output {
        Self {
            y: (self.y as f64 / rhs).floor() as u16,
            j: (self.j as f64 / rhs).floor() as u16,
            f: (self.f as f64 / rhs).floor() as u16,
        }
    }
}
