import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.feather as feather

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
with open('routes', 'wb') as f:
    feather.write_feather(table, f)