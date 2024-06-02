use crate::route::demand::pax::PaxDemand;
use crate::utils::ParseError;
use rkyv::{self, Deserialize};
use std::fs::File;
use std::io::Read;

const AIRPORT_COUNT: usize = 3907;
const ROUTE_COUNT: usize = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;

#[derive(Debug)]
pub struct Routes {
    pub demands: Vec<PaxDemand>,
}

impl Routes {
    pub fn from(file_path: &str) -> Result<Self, ParseError> {
        let mut file = File::open(file_path)?;
        let mut buffer = Vec::<u8>::new();
        file.read_to_end(&mut buffer)?;

        // ensure serialised bytes can be deserialised
        let archived = rkyv::check_archived_root::<Vec<PaxDemand>>(&buffer)
            .map_err(|e| ParseError::ArchiveError(e.to_string()))?;

        let demands: Vec<PaxDemand> = archived
            .deserialize(&mut rkyv::Infallible)
            .map_err(|e| ParseError::DeserialiseError(e.to_string()))?;

        if demands.len() != ROUTE_COUNT {
            return Err(ParseError::InvalidDataLength {
                expected: ROUTE_COUNT,
                actual: demands.len(),
            });
        }

        Ok(Routes { demands })
    }
}
