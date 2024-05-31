use once_cell::sync::Lazy;

use am4::aircraft::search::{Aircrafts, AircraftsIndex};
// use am4::user::{GameMode, Role, User};
use rstest::*;

#[fixture]
fn aircraft_data() -> AircraftsIndex<'static> {
    static AIRCRAFTS: Lazy<Aircrafts> =
        Lazy::new(|| Aircrafts::from_csv("./data/aircrafts.csv").unwrap());

    AIRCRAFTS.indexed()
}

#[rstest]
#[case("id:1", "b744")]
#[case("shortname:b744", "b744")]
#[case("name:B747-400", "b744")]
fn test_aircraft_search(
    aircraft_data: AircraftsIndex<'static>,
    #[case] inp: &str,
    #[case] expected_shortname: &str,
) {
    let ac = aircraft_data.search(inp).unwrap();
    assert_eq!(ac.aircraft.shortname.0, expected_shortname);
}

#[rstest]
#[case("b7440", "b744")]
#[case("B747-4000", "b744")]
#[case("shortname:b7440", "b744")]
#[case("name:B747-4000", "b744")]
#[case("shortname:b747-4000", "b744")] // cross suggest with name
#[case("name:b744", "b744")] // cross suggest with shortname
fn test_aircraft_fail_and_suggest(
    aircraft_data: AircraftsIndex<'static>,
    #[case] inp: &str,
    #[case] expected_shortname: &str,
) {
    let ac_result = aircraft_data.search(inp);
    assert!(ac_result.is_err());

    let suggs = aircraft_data.suggest(inp);
    assert!(suggs.is_ok());
    assert_eq!(suggs.unwrap()[0].item.shortname.0, expected_shortname);
}

#[rstest]
#[case("74sp")]
#[case("id:335a")]
fn test_aircraft_stoi_trailing(aircraft_data: AircraftsIndex<'static>, #[case] inp: &str) {
    let result = aircraft_data.search(inp);
    assert!(result.is_err());
}

#[rstest]
#[case("65590")]
#[case("id:65590")]
fn test_aircraft_stoi_overflow(aircraft_data: AircraftsIndex<'static>, #[case] inp: &str) {
    let result = aircraft_data.search(inp);
    assert!(result.is_err());
}

#[rstest]
#[case("b744[0]", "b744", 0, false, false, false, false)]
#[case("b744[1]", "b744", 1, false, false, false, false)]
#[case("b744[f1c]", "b744", 1, false, true, true, false)]
#[case("b744[cf]", "b744", 0, false, true, true, false)]
#[case("b744[sfcx]", "b744", 0, true, true, true, true)]
#[case("b744[s,fc,,  , ,x]", "b744", 0, true, true, true, true)]
#[case("id:1[sfcx]", "b744", 0, true, true, true, true)]
#[case("shortname:b744[sfcx]", "b744", 0, true, true, true, true)]
#[case("name:B747-400[sfcx]", "b744", 0, true, true, true, true)]
fn test_aircraft_modifiers_syntax(
    aircraft_data: AircraftsIndex<'static>,
    #[case] inp: &str,
    #[case] expected_shortname: &str,
    #[case] expected_engine: u8,
    #[case] expected_speed_mod: bool,
    #[case] expected_fuel_mod: bool,
    #[case] expected_co2_mod: bool,
    #[case] expected_fourx_mod: bool,
) {
    let result = aircraft_data.search(inp).unwrap();
    assert_eq!(result.aircraft.shortname.0, expected_shortname);

    // Check modifiers
    let mods = &result.modifiers;
    assert_eq!(mods.engine.0, expected_engine);
    assert_eq!(
        mods.mods.contains(&am4::aircraft::custom::Modifier::Speed),
        expected_speed_mod
    );
    assert_eq!(
        mods.mods.contains(&am4::aircraft::custom::Modifier::Fuel),
        expected_fuel_mod
    );
    assert_eq!(
        mods.mods.contains(&am4::aircraft::custom::Modifier::Co2),
        expected_co2_mod
    );
    assert_eq!(
        mods.mods.contains(&am4::aircraft::custom::Modifier::FourX),
        expected_fourx_mod
    );
}

#[rstest]
fn test_aircraft_engine_modifier(aircraft_data: AircraftsIndex<'static>) {
    let a = aircraft_data.search("b744").unwrap().aircraft;
    let a0 = aircraft_data.search("b744[0]").unwrap().aircraft;
    let a1 = aircraft_data.search("b744[1]").unwrap().aircraft;
    let a1sfc = aircraft_data.search("b744[1,sfc]").unwrap().aircraft;

    assert_eq!(a.id, a0.id);
    assert_eq!(a0.id, a1.id);
    assert_eq!(a.eid, a0.eid);
    assert_eq!(a1.fuel, 21.21);
    assert_eq!(a1.co2, 0.18);

    assert!(
        (a1sfc.speed / a1.speed - 1.1).abs() < 0.001,
        "Speed modifier not applied correctly"
    );
    assert!(
        (a1sfc.fuel / a1.fuel - 0.9).abs() < 0.001,
        "Fuel modifier not applied correctly"
    );
    assert!(
        (a1sfc.co2 / a1.co2 - 0.9).abs() < 0.001,
        "CO2 modifier not applied correctly"
    );
}

#[rstest]
fn test_aircraft_fourx(aircraft_data: AircraftsIndex<'static>) {
    let a0 = aircraft_data.search("b744").unwrap().aircraft;

    let a1 = aircraft_data.search("b744[x]").unwrap().aircraft;

    assert!(
        (a1.speed / a0.speed - 4.0).abs() < 0.001,
        "4x modifier not applied correctly"
    );
}
