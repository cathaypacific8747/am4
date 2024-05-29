use am4::airport::Airports;
use std::rc::Rc; // 0.8
use std::time::Instant;

fn main() {
    // NOTE: directory is CWD, not the location of the executable.
    let airports = Airports::from_csv("am4/data/airports.csv").unwrap();
    // println!("{:#?}", airports);

    // let a1 = airports.search("vhhh");
    // let a2 = airports.search("iata:hkg");
    // println!("{:?}", Rc::ptr_eq(a1.unwrap(), a2.unwrap()));

    // println!("{:#?}", y);
    // println!("{:#?}", y2);
    // print their address let y: Result<Option<&Rc<Airport>>, Error>

    let x = airports.suggest("vhhh");
    println!("{:?}", x);
}
