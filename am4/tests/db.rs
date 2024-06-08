use am4::aircraft::db::Aircrafts;
use am4::airport::db::Airports;
use am4::route::db::{Demands, Distances};
use am4::{AC_FILENAME, AP_FILENAME, DEM_FILENAME0, DEM_FILENAME1};
use once_cell::sync::Lazy;
use std::fs::File;
use std::io::Read;

pub fn get_bytes(path: &str) -> Result<Vec<u8>, std::io::Error> {
    let fp = "./data".to_string() + path;
    let mut file = File::open(fp)?;
    let mut buffer = Vec::<u8>::new();
    file.read_to_end(&mut buffer)?;
    Ok(buffer)
}

#[allow(dead_code)]
pub static AIRCRAFTS: Lazy<Aircrafts> =
    Lazy::new(|| Aircrafts::from_bytes(&get_bytes(AC_FILENAME).unwrap()).unwrap());

#[allow(dead_code)]
pub static AIRPORTS: Lazy<Airports> =
    Lazy::new(|| Airports::from_bytes(&get_bytes(AP_FILENAME).unwrap()).unwrap());

#[allow(dead_code)]
pub static ROUTES: Lazy<Demands> = Lazy::new(|| {
    let mut buf = get_bytes(DEM_FILENAME0).unwrap();
    let b1 = get_bytes(DEM_FILENAME1).unwrap();
    buf.extend(b1);
    Demands::from_bytes(&buf).unwrap()
});

#[allow(dead_code)]
pub static DISTANCES: Lazy<Distances> = Lazy::new(|| Distances::from_airports(&(*AIRPORTS.data())));
