pub mod config;
pub mod db;
pub mod demand;
pub mod search;
pub mod ticket;

mod distance;
mod speed;
mod time;

pub use distance::{Distance, ValidationError as DistanceError};
pub use speed::Speed;
pub use time::{FlightTime, ValidationError as FlightTimeError};
// TODO: impl std::ops::{Div, Mul} between v, s, t

mod ci;
pub use ci::{Ci, ValidationError as CiError};
