mod demand;

use bincode;
use demand::pax::PaxDemand;
use std::fs::File;
use thiserror::Error;

const AIRPORT_COUNT: usize = 3907;
const ROUTE_COUNT: usize = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;
const MAGIC_HEADER: &[u8; 3] = b"AM4";
const VERSION: u8 = 1;

#[derive(Debug)]
pub struct Routes {
    pub demands: Vec<PaxDemand>,
}

#[derive(Error, Debug)]
pub enum RouteError {
    #[error("Invalid data length: expected at least {expected} bits, got {actual}")]
    InvalidDataLength { expected: usize, actual: usize },
    #[error("Invalid magic header")]
    UnknownFile,
    #[error("Unsupported version: {0}")]
    UnsupportedVersion(u8),
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Bincode error: {0}")]
    BincodeError(#[from] bincode::Error),
}

impl Routes {
    pub fn from_file(file_path: &str) -> Result<Self, RouteError> {
        let file = File::open(file_path)?;

        let demands: Vec<PaxDemand> = bincode::deserialize_from(file)?;

        Ok(Routes { demands })
    }

    pub fn from_bytes(bytes: &[u8]) -> Result<Self, RouteError> {
        if bytes[..3] != *MAGIC_HEADER {
            return Err(RouteError::UnknownFile);
        }

        if bytes[3] != VERSION {
            return Err(RouteError::UnsupportedVersion(bytes[3]));
        }

        unimplemented!();
    }
}
