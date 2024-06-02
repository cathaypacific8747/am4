use once_cell::sync::Lazy;

use am4::route::db::Routes;
use am4::route::demand::pax::PaxDemand;
use rstest::*;

static ROUTES: Lazy<Routes> = Lazy::new(|| Routes::from("./data/routes.bin").unwrap());

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
