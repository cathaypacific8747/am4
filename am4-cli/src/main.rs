use am4::aircraft::search::Aircrafts;
// use am4::airport::search::Airports;

// NOTE: directory is CWD, not the location of the executable.
fn main() {
    // let airports = Airports::from_csv("am4/data/airports.csv").unwrap();
    // let index = airports.indexed();

    // println!("{:#?}", index.search("iata:hkg"));
    // println!("{:#?}", index.suggest("vhhx"));

    // let maxln = airports.data.iter().max_by_key(|a| a.name.0.len()).unwrap();
    // println!("{:#?}", maxln.name.0.len());

    let aircrafts = Aircrafts::from_csv("am4/data/aircrafts.csv").unwrap();
    let index = aircrafts.indexed();
    // println!("{:#?}", index.search("name:B747-4000"));
    println!("{:#?}", index.suggest("shortname:b7440"));
}
