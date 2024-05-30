import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.parquet as pq


def convert_routes():
    table = csv.read_csv(
        "../private/web/routes.fixed2.csv",
        csv.ReadOptions(column_names=["oid", "did", "yd", "jd", "fd", "d", "rwy"]),
    )
    table = table.cast(
        pa.schema(
            [
                ("oid", pa.uint16()),
                ("did", pa.uint16()),
                ("yd", pa.uint16()),
                ("jd", pa.uint16()),
                ("fd", pa.uint16()),
                ("d", pa.float64()),
                ("rwy", pa.uint16()),
            ]
        )
    )
    table = table.drop_columns(["oid", "did", "rwy"])
    pq.write_table(table, "routes.parquet")


def convert_airports():
    table = csv.read_csv(
        "../private/web/airports.csv",
    )
    # id,name,fullname,country,continent,iata,icao,lat,lng,rwy,market,hub_cost,rwy_codes
    table = table.cast(
        pa.schema(
            [
                ("id", pa.uint16()),
                ("name", pa.string()),
                ("fullname", pa.string()),
                ("country", pa.string()),
                ("continent", pa.string()),
                ("iata", pa.string()),
                ("icao", pa.string()),
                ("lat", pa.float64()),
                ("lng", pa.float64()),
                ("rwy", pa.uint16()),
                ("market", pa.uint8()),
                ("hub_cost", pa.uint32()),
                ("rwy_codes", pa.string()),
            ]
        )
    )
    pq.write_table(table, "airports.parquet")
    csv.write_csv(table, "airports.csv")


def convert_aircrafts():
    table = csv.read_csv(
        "../private/web/aircrafts.new.csv",
    )
    # id,shortname,manufacturer,name,type,priority,eid,ename,speed,fuel,co2,cost,capacity,rwy,check_cost,range,ceil,maint,pilots,crew,engineers,technicians,img,wingspan,length
    print(table.schema)
    table = table.cast(
        pa.schema(
            [
                ("id", pa.uint16()),
                ("shortname", pa.string()),
                ("manufacturer", pa.string()),
                ("name", pa.string()),
                ("type", pa.uint8()),
                ("priority", pa.uint8()),
                ("eid", pa.uint16()),
                ("ename", pa.string()),
                ("speed", pa.float32()),
                ("fuel", pa.float32()),
                ("co2", pa.float32()),
                ("cost", pa.uint32()),
                ("capacity", pa.uint32()),
                ("rwy", pa.uint16()),
                ("check_cost", pa.uint32()),
                ("range", pa.uint16()),
                ("ceil", pa.uint16()),
                ("maint", pa.uint16()),
                ("pilots", pa.uint8()),
                ("crew", pa.uint8()),
                ("engineers", pa.uint8()),
                ("technicians", pa.uint8()),
                ("img", pa.string()),
                ("wingspan", pa.uint8()),
                ("length", pa.uint8()),
            ]
        )
    )
    pq.write_table(table, "aircrafts.parquet")

    # for serde
    type_mapping = {0: "pax", 1: "cargo", 2: "vip"}
    type_array = pa.array(
        [type_mapping[i] if i in type_mapping else None for i in table.column("type").to_pylist()], type=pa.string()
    )
    table = table.remove_column(table.schema.get_field_index("type"))
    table = table.add_column(4, "type", type_array)
    csv.write_csv(table, "aircrafts.csv")


if __name__ == "__main__":
    # convert_routes()
    convert_airports()
    convert_aircrafts()
