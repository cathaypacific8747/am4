mod db;
use db::{DEMAND_MATRIX, DISTANCE_MATRIX};

use am4::route::db::ROUTE_COUNT;
use am4::route::demand::PaxDemand;
use rstest::*;

#[rstest]
fn test_routes_ok() {
    assert_eq!(DEMAND_MATRIX.data().len(), ROUTE_COUNT);
    let expected = PaxDemand {
        y: 542,
        j: 182,
        f: 45,
    };
    assert_eq!(&DEMAND_MATRIX.data()[0], &expected);
    assert_eq!(&DEMAND_MATRIX[(0, 1)], &expected);
}

#[rstest]
fn test_distances_ok() {
    assert_eq!(DISTANCE_MATRIX.data().len(), ROUTE_COUNT);
    assert_eq!(
        DISTANCE_MATRIX.data()[0].get().to_bits(),
        330.21942_f32.to_bits()
    ); // 1 -> 2
    assert_eq!(
        DISTANCE_MATRIX.data()[1].get().to_bits(),
        1_245.811_6_f32.to_bits()
    ); // 1 -> 3
}
