use once_cell::sync::Lazy;

use am4::airport::search::{Airports, AirportsIndex};
use rstest::*;

#[fixture]
fn airport_data() -> AirportsIndex<'static> {
    static AIRPORTS: Lazy<Airports> =
        Lazy::new(|| Airports::from_csv("./data/airports.csv").unwrap());

    AIRPORTS.indexed()
}

#[rstest]
#[case("id:3500", "HKG")]
#[case("iata:Hkg", "HKG")]
#[case("icao:vhhh", "HKG")]
#[case("name:hong kong", "HKG")]
#[case("hong kong", "HKG")]
fn test_airport_search(
    airport_data: AirportsIndex<'static>,
    #[case] inp: &str,
    #[case] iata: &str,
) {
    let ap = airport_data.search(inp).unwrap();
    assert_eq!(ap.iata.0, iata);
}

#[rstest]
#[case("VHHX  ", "HKG")]
#[case("hkgA", "HKG")]
#[case("VHHx", "HKG")]
#[case("hong kongg", "HKG")]
#[case("icao:hkgg", "HKG")] // cross suggest with iata
#[case("iata:vhhx", "HKG")] // cross suggest with icao
#[case("name:vhhx", "HKG")] // cross suggest with icao
fn test_airport_fail_and_suggest(
    airport_data: AirportsIndex<'static>,
    #[case] inp: &str,
    #[case] iata: &str,
) {
    let ap_result = airport_data.search(inp);
    assert!(ap_result.is_err());

    let suggs = airport_data.suggest(inp);
    assert!(suggs.is_ok());
    assert_eq!(suggs.unwrap()[0].item.iata.0, iata);
}

#[rstest]
#[case("65590")]
#[case("id:65590")]
fn test_airport_stoi_overflow(airport_data: AirportsIndex<'static>, #[case] inp: &str) {
    let result = airport_data.search(inp);
    assert!(result.is_err());
}
