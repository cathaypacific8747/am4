use crate::route::demand::pax::PaxDemand;
use crate::utils::ParseError;
use rkyv::{self, Deserialize};

const AIRPORT_COUNT: usize = 3907;
const ROUTE_COUNT: usize = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;

#[derive(Debug)]
pub struct Routes {
    pub demands: Vec<PaxDemand>,
}

impl Routes {
    pub fn from_bytes(buffer: &Vec<u8>) -> Result<Self, ParseError> {
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
