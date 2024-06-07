use crate::airport::{Airport, Point};

const EARTH_RADIUS_KM: f32 = 6371.0;

#[inline]
pub fn calculate_distance(origin: &Point, destination: &Point) -> f32 {
    let lat1 = origin.lat.to_radians();
    let lon1 = origin.lng.to_radians();
    let lat2 = destination.lat.to_radians();
    let lon2 = destination.lng.to_radians();

    let dlat = lat2 - lat1;
    let dlon = lon2 - lon1;

    let a = (dlat / 2.0).sin().powi(2) + lat1.cos() * lat2.cos() * (dlon / 2.0).sin().powi(2);
    let c = 2.0 * a.sqrt().asin();

    EARTH_RADIUS_KM * c
}

#[derive(Debug, PartialEq)]
pub struct Leg<'a> {
    origin: &'a Airport,
    destination: &'a Airport,
    distance: f32,
}
