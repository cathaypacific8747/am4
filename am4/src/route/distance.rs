use crate::airport::{Airport, Point};

const EARTH_RADIUS_KM: f32 = 6371.0;

impl Point {
    #[inline]
    pub fn distance_to(&self, other: &Point) -> f32 {
        let lat1 = self.lat.to_radians();
        let lon1 = self.lng.to_radians();

        let lat2 = other.lat.to_radians();
        let lon2 = other.lng.to_radians();

        let dlat = lat2 - lat1;
        let dlon = lon2 - lon1;

        let a = (dlat / 2.0).sin().powi(2) + lat1.cos() * lat2.cos() * (dlon / 2.0).sin().powi(2);
        let c = 2.0 * a.sqrt().asin();

        EARTH_RADIUS_KM * c
    }
}

impl Airport {
    pub fn distance_to(&self, other: &Airport) -> f32 {
        self.location.distance_to(&other.location)
    }
}
