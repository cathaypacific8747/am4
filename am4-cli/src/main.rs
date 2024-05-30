// use am4::aircraft::Aircrafts;
use am4::airport::Airports;
// use std::rc::Rc;

fn main() {
    // NOTE: directory is CWD, not the location of the executable.
    let airports = Airports::from_csv("am4/data/airports.csv").unwrap();
    // println!("{:#?}", airports);

    let a1 = airports.search("iata:hkgA");
    let suggestions = airports.suggest("iata:hkgA");

    println!("{:#?}", suggestions)

    // let x = airports.suggest("vhhh");
    // println!("{:?}", x);

    // let aircrafts = Aircrafts::from_csv("am4/data/aircrafts.csv").unwrap();
    // println!("{:#?}", aircrafts);
    // println!("{:#?}", aircrafts.by_id.len());
    // println!("{:#?}", aircrafts.search("a388[s]").unwrap());
    // println!("{:#?}", aircrafts.search_variants("a388").unwrap());
}
