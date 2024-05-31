use am4::aircraft::{self, Aircrafts, AircraftsIndex};
// use am4::airport::Airports;
// use std::rc::Rc;

fn main() {
    // NOTE: directory is CWD, not the location of the executable.
    // let airports = Airports::from_csv("am4/data/airports.csv").unwrap();
    // println!("{:#?}", airports);

    // let a1 = airports.search("iata:hkgA");
    // let suggestions = airports.suggest("iata:hkgA");

    // println!("{:#?}", suggestions)

    let binding = Aircrafts::from_csv("am4/data/aircrafts.csv").unwrap();
    let aircrafts = binding.indexed();
    println!("{:#?}", aircrafts.search("a388[s]"));
    println!("{:#?}", aircrafts.search("a388"));
}
