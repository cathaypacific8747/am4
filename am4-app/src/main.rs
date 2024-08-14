#![allow(unused)]

use am4::aircraft::db::Aircrafts;
use am4::airport::db::Airports;
use am4::airport::{self, Airport};
use am4::route::db::Demands;
use am4::route::search::RouteSearch;
use am4::{AC_FILENAME, AP_FILENAME, DEM_FILENAME0, DEM_FILENAME1};
use std::fs::File;
use std::io::Read;

fn get_bytes(path: &str) -> Result<Vec<u8>, std::io::Error> {
    let fp = env!("CARGO_MANIFEST_DIR").to_string() + "/../am4/assets/" + path;
    let mut file = File::open(fp)?;
    let mut buffer = Vec::<u8>::new();
    file.read_to_end(&mut buffer)?;
    Ok(buffer)
}

fn get_demands() -> Demands {
    let mut buf = get_bytes(DEM_FILENAME0).unwrap();
    let b1 = get_bytes(DEM_FILENAME1).unwrap();
    buf.extend(b1);
    Demands::from_bytes(&buf).unwrap()
}

fn main() {
    let aircrafts = Aircrafts::from_bytes(&get_bytes(AC_FILENAME).unwrap()).unwrap();
    let airports = Airports::from_bytes(&get_bytes(AP_FILENAME).unwrap()).unwrap();
    let demands = get_demands();
    let origin = airports.search("HKG").unwrap();
    // let destinations = [
    //     airports.search("LHR").unwrap(),
    //     airports.search("HKG").unwrap(),
    // ];
    let destinations = airports.data();

    let search = RouteSearch::new(&airports, &demands, origin).unwrap();
    let data = search.create_abstract(destinations.as_slice());
    println!("{:#?}", data.len())
}
