mod db;
use db::ROUTES;

use am4::route::demand::pax::PaxDemand;
use rstest::*;

#[rstest]
fn test_routes_ok() {
    assert_eq!(ROUTES.demands.len(), 3907 * 3906 / 2);
    assert_eq!(
        ROUTES.demands[0],
        PaxDemand {
            y: 542,
            j: 182,
            f: 45
        }
    );
}
