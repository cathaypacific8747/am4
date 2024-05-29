use am4::airport::Airports;

fn main() {
    // NOTE: directory is CWD, not the location of the executable.
    let airports = Airports::from_csv("am4/data/airports.csv").unwrap();
    // println!("{:#?}", airports);

    let y = airports.search("hkg");
    println!("{:#?}", y);
}
