mod utils;

use polars::frame::row::Row;
use polars::prelude::*;
use std::io::Write;
use std::str::FromStr;
use utils::*;

fn convert_routes() {
    use am4::route::demand::pax::PaxDemand;

    let mut schema = Schema::new();
    schema.with_column("oid".into(), DataType::UInt32);
    schema.with_column("did".into(), DataType::UInt16);
    schema.with_column("yd".into(), DataType::UInt16);
    schema.with_column("jd".into(), DataType::UInt16);
    schema.with_column("fd".into(), DataType::UInt16);
    schema.with_column("d".into(), DataType::Float64);
    schema.with_column("rwy".into(), DataType::UInt16);

    let lf = LazyCsvReader::new("../../private/web/routes.fixed2.csv")
        .with_has_header(false)
        .with_schema(Some(Arc::new(schema)))
        .finish()
        .unwrap();

    // v0.1
    // let mut df = lf.drop(vec!["oid", "did", "rwy"]).collect().unwrap();
    // let mut file = std::fs::File::create("routes.parquet").unwrap();
    // ParquetWriter::new(&mut file).finish(&mut df).unwrap();
    // dbg!(df);

    // v0.2
    let df = &lf.drop(vec!["oid", "did", "d", "rwy"]).collect().unwrap();
    let num_rows = df.height();

    let mut dems = Vec::<PaxDemand>::with_capacity(num_rows);
    let mut row = Row::new(vec![AnyValue::UInt16(0); 3]);
    for i in 0..num_rows {
        df.get_row_amortized(i, &mut row).unwrap();
        let yjf = row
            .0
            .iter()
            .map(|v| match v {
                AnyValue::UInt16(v) => *v,
                _ => unreachable!(),
            })
            .collect::<Vec<u16>>();

        dems.push(PaxDemand {
            y: yjf[0],
            j: yjf[1],
            f: yjf[2],
        });

        if i % 1_000_000 == 0 {
            println!("processed {i} / {num_rows}");
        }
    }
    let mut file = std::fs::File::create("routes.bin").unwrap();
    let b = rkyv::to_bytes::<Vec<PaxDemand>, 45_782_236>(&dems).unwrap();
    file.write_all(&b).unwrap();

    println!("wrote {:?} bytes to {:?}", b.len(), file);
}

fn convert_airports() {
    use am4::airport::{Airport, Iata, Icao, Id, Name};

    let mut schema = Schema::new();
    schema.with_column("id".into(), DataType::UInt16);
    schema.with_column("name".into(), DataType::String);
    schema.with_column("fullname".into(), DataType::String);
    schema.with_column("country".into(), DataType::String);
    schema.with_column("continent".into(), DataType::String);
    schema.with_column("iata".into(), DataType::String);
    schema.with_column("icao".into(), DataType::String);
    schema.with_column("lat".into(), DataType::Float64);
    schema.with_column("lng".into(), DataType::Float64);
    schema.with_column("rwy".into(), DataType::UInt16);
    schema.with_column("market".into(), DataType::UInt8);
    schema.with_column("hub_cost".into(), DataType::UInt32);
    schema.with_column("rwy_codes".into(), DataType::String);

    let lf = LazyCsvReader::new("../../private/web/airports.new.csv")
        .with_has_header(true)
        .with_schema(Some(Arc::new(schema)))
        .finish()
        .unwrap();

    let df = &lf.collect().unwrap();
    // v0.1
    // let mut file = std::fs::File::create("routes.parquet").unwrap();
    // ParquetWriter::new(&mut file).finish(&mut df).unwrap();
    // dbg!(df);

    let num_rows = df.height();
    let mut airports = Vec::<Airport>::with_capacity(num_rows);
    for i in 0..num_rows {
        // not using amortized version - slow!
        let r = df.get_row(i).unwrap().0;

        airports.push(Airport {
            id: Id(get_u16(r[0].clone())),
            name: Name::from_str(get_str(r[1].clone())).unwrap(),
            fullname: get_str(r[2].clone()).to_string(),
            country: get_str(r[3].clone()).to_string(),
            continent: get_str(r[4].clone()).to_string(),
            iata: Iata::from_str(get_str(r[5].clone())).unwrap(),
            icao: Icao::from_str(get_str(r[6].clone())).unwrap(),
            lat: get_f64(r[7].clone()),
            lng: get_f64(r[8].clone()),
            rwy: get_u16(r[9].clone()),
            market: get_u8(r[10].clone()),
            hub_cost: get_u32(r[11].clone()),
            rwy_codes: get_str(r[12].clone())
                .split('|')
                .map(|s| s.to_string())
                .collect(),
        });
    }
    println!("{:?}", airports.len());
    let mut file = std::fs::File::create("airports.bin").unwrap();
    let b = rkyv::to_bytes::<Vec<Airport>, 514040>(&airports).unwrap();
    file.write_all(&b).unwrap();

    println!("wrote {:?} bytes to {:?}", b.len(), file);
}

fn convert_aircrafts() {
    use am4::aircraft::{Aircraft, AircraftType, EnginePriority, Id, Name, ShortName};

    let mut schema = Schema::new();
    schema.with_column("id".into(), DataType::UInt16);
    schema.with_column("shortname".into(), DataType::String);
    schema.with_column("manufacturer".into(), DataType::String);
    schema.with_column("name".into(), DataType::String);
    schema.with_column("type".into(), DataType::UInt8);
    schema.with_column("priority".into(), DataType::UInt8);
    schema.with_column("eid".into(), DataType::UInt16);
    schema.with_column("ename".into(), DataType::String);
    schema.with_column("speed".into(), DataType::Float32);
    schema.with_column("fuel".into(), DataType::Float32);
    schema.with_column("co2".into(), DataType::Float32);
    schema.with_column("cost".into(), DataType::UInt32);
    schema.with_column("capacity".into(), DataType::UInt32);
    schema.with_column("rwy".into(), DataType::UInt16);
    schema.with_column("check_cost".into(), DataType::UInt32);
    schema.with_column("range".into(), DataType::UInt16);
    schema.with_column("ceil".into(), DataType::UInt16);
    schema.with_column("maint".into(), DataType::UInt16);
    schema.with_column("pilots".into(), DataType::UInt8);
    schema.with_column("crew".into(), DataType::UInt8);
    schema.with_column("engineers".into(), DataType::UInt8);
    schema.with_column("technicians".into(), DataType::UInt8);
    schema.with_column("img".into(), DataType::String);
    schema.with_column("wingspan".into(), DataType::UInt8);
    schema.with_column("length".into(), DataType::UInt8);

    let lf = LazyCsvReader::new("../../private/web/aircrafts.new.csv")
        .with_has_header(true)
        .with_schema(Some(Arc::new(schema)))
        .finish()
        .unwrap();
    let df = &lf.collect().unwrap();

    let num_rows = df.height();
    let mut aircrafts = Vec::<Aircraft>::with_capacity(num_rows);

    for i in 0..num_rows {
        let r = df.get_row(i).unwrap().0;

        aircrafts.push(Aircraft {
            id: Id(get_u16(r[0].clone())),
            shortname: ShortName::from_str(get_str(r[1].clone())).unwrap(),
            manufacturer: get_str(r[2].clone()).to_string(),
            name: Name::from_str(get_str(r[3].clone())).unwrap(),
            ac_type: match get_u8(r[4].clone()) {
                0 => AircraftType::Pax,
                1 => AircraftType::Cargo,
                2 => AircraftType::Vip,
                _ => panic!("unknown aircraft type"),
            },
            priority: EnginePriority(get_u8(r[5].clone())),
            eid: get_u16(r[6].clone()),
            ename: get_str(r[7].clone()).to_string(),
            speed: get_f32(r[8].clone()),
            fuel: get_f32(r[9].clone()),
            co2: get_f32(r[10].clone()),
            cost: get_u32(r[11].clone()),
            capacity: get_u32(r[12].clone()),
            rwy: get_u16(r[13].clone()),
            check_cost: get_u32(r[14].clone()),
            range: get_u16(r[15].clone()),
            ceil: get_u16(r[16].clone()),
            maint: get_u16(r[17].clone()),
            pilots: get_u8(r[18].clone()),
            crew: get_u8(r[19].clone()),
            engineers: get_u8(r[20].clone()),
            technicians: get_u8(r[21].clone()),
            img: get_str(r[22].clone()).to_string(),
            wingspan: get_u8(r[23].clone()),
            length: get_u8(r[24].clone()),
        });
    }
    let mut file = std::fs::File::create("aircrafts.bin").unwrap();
    let b = rkyv::to_bytes::<Vec<Aircraft>, 68200>(&aircrafts).unwrap();
    file.write_all(&b).unwrap();

    println!("wrote {:?} bytes to {:?}", b.len(), file);
}

fn main() {
    convert_routes();
    convert_airports();
    convert_aircrafts();
}
