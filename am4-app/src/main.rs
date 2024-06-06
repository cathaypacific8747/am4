// use am4::aircraft::db::Aircrafts;
use am4::airport::db::Airports;
use std::fs::File;
use std::io::Read;

fn get_bytes(path: &str) -> Result<Vec<u8>, std::io::Error> {
    let mut file = File::open(path)?;
    let mut buffer = Vec::<u8>::new();
    file.read_to_end(&mut buffer)?;
    Ok(buffer)
}

fn main() {
    let airports = Airports::from_bytes(&get_bytes("../am4/data/airports.bin").unwrap()).unwrap();
    // let aircrafts = Aircrafts::from_bytes(&get_bytes("../am4/data/aircrafts.bin").unwrap()).unwrap();

    dbg!(airports.search("HKG").unwrap());
}
