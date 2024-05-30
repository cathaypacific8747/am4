// use am4::airport::Airports;
use am4::aircraft::Aircrafts;
// use std::rc::Rc;

fn main() {
    // NOTE: directory is CWD, not the location of the executable.
    // let airports = Airports::from_csv("am4/data/airports.csv").unwrap();
    // println!("{:#?}", airports);

    // let a1 = airports.search("vhhh");
    // let a2 = airports.search("iata:hkg");
    // println!("{:?}", Rc::ptr_eq(a1.unwrap(), a2.unwrap()));
    // println!("{:#?} {:#?}", y, y2);

    // let x = airports.suggest("vhhh");
    // println!("{:?}", x);

    let aircrafts = Aircrafts::from_csv("am4/data/aircrafts.csv").unwrap();
    // println!("{:#?}", aircrafts);
    println!("{:#?}", aircrafts.search("a388").unwrap());
    println!("{:#?}", aircrafts.search("a388[sfc]").unwrap());
}
