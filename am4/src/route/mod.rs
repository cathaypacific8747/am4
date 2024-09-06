use std::ops::{Div, Mul};

pub mod config;
pub mod db;
pub mod demand;
pub mod search;
pub mod ticket;

mod distance;
mod speed;
mod time;

pub use distance::{Distance, DistanceError};
pub use speed::Speed;
pub use time::{FlightTime, FlightTimeError};

macro_rules! impl_mul {
    ($lhs:ty, $rhs:ty, $output:ty) => {
        impl Mul<$rhs> for $lhs {
            type Output = $output;

            fn mul(self, rhs: $rhs) -> Self::Output {
                Self::Output::new_unchecked(self.get() * rhs.get())
            }
        }
    };
}

macro_rules! impl_div {
    ($lhs:ty, $rhs:ty, $output:ty) => {
        impl Div<$rhs> for $lhs {
            type Output = $output;

            fn div(self, rhs: $rhs) -> Self::Output {
                Self::Output::new_unchecked(self.get() / rhs.get())
            }
        }
    };
}

impl_div!(Distance, FlightTime, Speed);
impl_mul!(Speed, FlightTime, Distance);
impl_mul!(FlightTime, Speed, Distance);
impl_div!(Distance, Speed, FlightTime);

mod ci;
pub use ci::{Ci, ValidationError as CiError};
