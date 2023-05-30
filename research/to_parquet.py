import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.parquet as pq

def convert_routes():
    table = csv.read_csv(
        'routes.csv',
        csv.ReadOptions(column_names=["oid", "did", "yd", "jd", "fd", "d"]),
    )
    table = table.cast(pa.schema([
        ("oid", pa.uint16()),
        ("did", pa.uint16()),
        ("yd", pa.uint16()),
        ("jd", pa.uint16()),
        ("fd", pa.uint16()),
        ("d", pa.float32()),
    ]))
    pq.write_table(table, 'routes.parquet')

def convert_airports():
    table = csv.read_csv(
        'airports.csv',
    )
    # id,name,fullname,country,continent,iata,icao,lat,lng,rwy,market,hub_cost,rwy_codes
    table = table.cast(pa.schema([
        ("id", pa.uint16()),
        ("name", pa.string()),
        ("fullname", pa.string()),
        ("country", pa.string()),
        ("continent", pa.string()),
        ("iata", pa.string()),
        ("icao", pa.string()),
        ("lat", pa.float32()),
        ("lng", pa.float32()),
        ("rwy", pa.uint16()),
        ("market", pa.uint8()),
        ("hub_cost", pa.uint32()),
        ("rwy_codes", pa.string()),
    ]))
    pq.write_table(table, 'airports.parquet')

if __name__ == '__main__':
    # convert_routes()
    convert_airports()