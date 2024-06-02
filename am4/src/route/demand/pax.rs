use rkyv;
use serde::{Deserialize, Serialize};

#[derive(
    Debug, PartialEq, Deserialize, Serialize, rkyv::Archive, rkyv::Serialize, rkyv::Deserialize,
)]
#[archive(check_bytes)]
pub struct PaxDemand {
    pub y: u16,
    pub j: u16,
    pub f: u16,
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
