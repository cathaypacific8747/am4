// use am4::aircraft::db::Aircrafts;
use am4::airport::db::Airports;
use am4::AP_FILENAME;
use std::fs::File;
use std::io::Read;

fn get_bytes(path: &str) -> Result<Vec<u8>, std::io::Error> {
    let fp = env!("CARGO_MANIFEST_DIR").to_string() + "/../am4/assets/" + path;
    let mut file = File::open(fp)?;
    let mut buffer = Vec::<u8>::new();
    file.read_to_end(&mut buffer)?;
    Ok(buffer)
}

fn main() {
    let airports = Airports::from_bytes(&get_bytes(AP_FILENAME).unwrap()).unwrap();
    dbg!(airports.search("HKG").unwrap());
    // let aircrafts = Aircrafts::from_bytes(&get_bytes(AC_FILENAME).unwrap()).unwrap();
}
