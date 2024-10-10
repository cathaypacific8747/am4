#![allow(unused)]

use am4::aircraft::db::Aircrafts;
use am4::airport::{self, db::Airports, Airport};
use am4::route::db::{DemandMatrix, DistanceMatrix};
use am4::route::search::{schedule::SearchConfig, AbstractConfig, AbstractRoute, Routes};
use am4::route::Distance;
use am4::user::GameMode;
use am4::utils::Filter;
use am4::{aircraft, AC_FILENAME, AP_FILENAME, DEM_FILENAME0, DEM_FILENAME1};
use std::fs::File;
use std::io::Read;

fn get_bytes(path: &str) -> Result<Vec<u8>, std::io::Error> {
    let fp = env!("CARGO_MANIFEST_DIR").to_string() + "/../am4/assets/" + path;
    let mut file = File::open(fp)?;
    let mut buffer = Vec::<u8>::new();
    file.read_to_end(&mut buffer)?;
    Ok(buffer)
}

fn get_demands() -> DemandMatrix {
    let mut buf = get_bytes(DEM_FILENAME0).unwrap();
    let b1 = get_bytes(DEM_FILENAME1).unwrap();
    buf.extend(b1);
    DemandMatrix::from_bytes(&buf).unwrap()
}

fn print_len<R, C>(id: &str, dests: &Routes<R, C>) {
    println!(
        "{id:>20} | ok: {:<4} | err: {:<4}",
        dests.routes().len(),
        dests.errors().len(),
    );
}

fn main() {
    let aircrafts = Aircrafts::from_bytes(&get_bytes(AC_FILENAME).unwrap()).unwrap();
    let airports = Airports::from_bytes(&get_bytes(AP_FILENAME).unwrap()).unwrap();
    let distances = DistanceMatrix::from_airports(airports.data());
    let demand_matrix = get_demands();

    let origin = airports.search("WLG").unwrap();
    let aircraft = aircrafts.search("mc214").unwrap();
    let search_config = SearchConfig {
        distance_filter: "..9000".parse().unwrap(),
        ..Default::default()
    };

    let abstract_routes = Routes::new(&airports, &distances, origin, airports.data());
    print_len("abstract", &abstract_routes);
    let concrete_routes = abstract_routes.with_aircraft(&aircraft.aircraft, &GameMode::Easy);
    print_len("concrete", &concrete_routes);
    let scheduled_routes = concrete_routes.schedule(&demand_matrix, &distances, &search_config);
    print_len("scheduled", &scheduled_routes);
}
