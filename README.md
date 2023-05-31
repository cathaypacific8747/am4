# AM4 bot

## Installation
Requirements: python3.11

```bash
pip3 install -r requirements.txt
```

## dev
cmake
```bash
virtualenv .venv
.venv/scripts/activate
pip3 install .[dev]
pip3 uninstall am4bot -y; pip3 install .
.venv/scripts/deactivate

mkdir build
cd build
cmake ..
cmake --build . --target am4utils

https://github.com/duckdb/duckdb/archive/refs/tags/v0.8.0.zip
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_GENERATOR_PLATFORM=x64 -DBUILD_ICU_EXTENSION=1 -DBUILD_PARQUET_EXTENSION=1 -DBUILD_TPCH_EXTENSION=1 -DBUILD_TPCDS_EXTENSION=1 -DBUILD_FTS_EXTENSION=1 -DBUILD_JSON_EXTENSION=1 -DBUILD_EXCEL_EXTENSION=0 -DBUILD_VISUALIZER_EXTENSION=1 -DBUILD_ODBC_DRIVER=1 -DDISABLE_UNITY=1 -DBUILD_AUTOCOMPLETE_EXTENSION=1 -DSTATIC_LIBCPP=1
cmake --build . --config Release
```

```sql
CREATE TABLE airports (
  id         USMALLINT PRIMARY KEY NOT NULL,
  name       VARCHAR NOT NULL,
  fullname   VARCHAR NOT NULL,
  country    VARCHAR NOT NULL,
  continent  VARCHAR NOT NULL,
  iata       VARCHAR UNIQUE NOT NULL,
  icao       VARCHAR UNIQUE NOT NULL,
  lat        DOUBLE NOT NULL,
  lng        DOUBLE NOT NULL,
  rwy        USMALLINT NOT NULL,
  market     UTINYINT NOT NULL,
  hub_cost   UINTEGER NOT NULL,
  rwy_codes  VARCHAR NOT NULL
);
INSERT INTO airports SELECT * FROM read_parquet('./src/am4utils/data/airports.parquet');

CREATE TABLE aircrafts AS SELECT * FROM read_parquet('./src/am4utils/data/aircrafts.parquet'); 
DESCRIBE TABLE aircrafts; 
-- ┌──────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
-- │ column_name  │ column_type │  null   │   key   │ default │  extra  │
-- │   varchar    │   varchar   │ varchar │ varchar │ varchar │ varchar │
-- ├──────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
-- │ id           │ USMALLINT   │ YES     │         │         │         │
-- │ name         │ VARCHAR     │ YES     │         │         │         │
-- │ manufacturer │ VARCHAR     │ YES     │         │         │         │
-- │ cargo        │ BOOLEAN     │ YES     │         │         │         │
-- │ eid          │ USMALLINT   │ YES     │         │         │         │
-- │ ename        │ VARCHAR     │ YES     │         │         │         │
-- │ speed        │ FLOAT       │ YES     │         │         │         │
-- │ fuel         │ FLOAT       │ YES     │         │         │         │
-- │ co2          │ FLOAT       │ YES     │         │         │         │
-- │ cost         │ UINTEGER    │ YES     │         │         │         │
-- │ capacity     │ UINTEGER    │ YES     │         │         │         │
-- │ rwy          │ USMALLINT   │ YES     │         │         │         │
-- │ check_cost   │ UINTEGER    │ YES     │         │         │         │
-- │ range        │ USMALLINT   │ YES     │         │         │         │
-- │ ceil         │ USMALLINT   │ YES     │         │         │         │
-- │ maint        │ USMALLINT   │ YES     │         │         │         │
-- │ pilots       │ UTINYINT    │ YES     │         │         │         │
-- │ crew         │ UTINYINT    │ YES     │         │         │         │
-- │ engines      │ UTINYINT    │ YES     │         │         │         │
-- │ technicians  │ UTINYINT    │ YES     │         │         │         │
-- │ img          │ VARCHAR     │ YES     │         │         │         │
-- │ wingspan     │ UTINYINT    │ YES     │         │         │         │
-- │ length       │ UTINYINT    │ YES     │         │         │         │
-- ├──────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┤
-- │ 23 rows                                                  6 columns │
-- └────────────────────────────────────────────────────────────────────┘

CREATE TABLE routes AS SELECT * FROM read_parquet('./src/am4utils/data/routes.parquet');
DESCRIBE TABLE routes;
-- ┌─────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
-- │ column_name │ column_type │  null   │   key   │ default │  extra  │
-- │   varchar   │   varchar   │ varchar │ varchar │ varchar │ varchar │
-- ├─────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
-- │ oid         │ USMALLINT   │ YES     │         │         │         │
-- │ did         │ USMALLINT   │ YES     │         │         │         │
-- │ yd          │ USMALLINT   │ YES     │         │         │         │
-- │ jd          │ USMALLINT   │ YES     │         │         │         │
-- │ fd          │ USMALLINT   │ YES     │         │         │         │
-- │ d           │ FLOAT       │ YES     │         │         │         │
-- └─────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘
```



```cpp
#include "duckdb.hpp"

duckdb::DuckDB db(nullptr);
duckdb::Connection con(db);

// create a table
con.Query("CREATE TABLE integers(i INTEGER, j INTEGER)");

// insert three rows into the table
con.Query("INSERT INTO integers VALUES (3, 4), (5, 6), (7, NULL)");

duckdb::unique_ptr<duckdb::MaterializedQueryResult> result = con.Query("SELECT * FROM integers");
if (result->HasError()) {
    std::cerr << result->GetError() << std::endl;
    return false;
}

```