use std::string::String;

#[derive(Debug, Clone, PartialEq)]
enum AircraftType {
    PAX,
    CARGO,
    VIP,
}

#[derive(Debug, Clone)]
struct Aircraft {
    id: u16,
    shortname: String,
    manufacturer: String,
    name: String,
    ac_type: AircraftType,
    priority: u8,
    eid: u16,
    ename: String,
    speed: f32,
    fuel: f32,
    co2: f32,
    cost: u32,
    capacity: u32,
    rwy: u16,
    check_cost: u32,
    range: u16,
    ceil: u16,
    maint: u16,
    pilots: u8,
    crew: u8,
    engineers: u8,
    technicians: u8,
    img: String,
    wingspan: u8,
    length: u8,
}

struct CustomAircraft {
    aircraft: Aircraft,
    fuel_mod: bool,
    co2_mod: bool,
    speed_mod: bool,
    fourx_mod: bool,
}

// #[derive(Debug, Clone, PartialEq)]
// enum SearchType {
//     ALL,
//     ID,
//     SHORTNAME,
//     NAME,
// }
