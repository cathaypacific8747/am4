mod db;
use db::{DISTANCES, ROUTES};

use am4::route::db::ROUTE_COUNT;
use am4::route::demand::pax::PaxDemand;
use rstest::*;

#[rstest]
fn test_routes_ok() {
    assert_eq!(ROUTES.data().len(), ROUTE_COUNT);
    let expected = PaxDemand {
        y: 542,
        j: 182,
        f: 45,
    };
    assert_eq!(&ROUTES.data()[0], &expected);
    assert_eq!(&ROUTES[(0, 1)], &expected);
}

#[rstest]
fn test_distances_ok() {
    assert_eq!(DISTANCES.data().len(), ROUTE_COUNT);
    assert_eq!(DISTANCES.data()[0].to_bits(), 330.21942_f32.to_bits()); // 1 -> 2
    assert_eq!(DISTANCES.data()[1].to_bits(), 1_245.811_6_f32.to_bits()); // 1 -> 3
}
