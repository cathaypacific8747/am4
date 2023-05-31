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
```

### duckdb
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
CREATE INDEX airports_idx ON airports(name, fullname, country, continent, lat, lng, rwy, market);


CREATE TABLE aircrafts (
  id           USMALLINT NOT NULL,
  name         VARCHAR NOT NULL,
  manufacturer VARCHAR NOT NULL,
  cargo        BOOLEAN NOT NULL,
  eid          USMALLINT NOT NULL,
  ename        VARCHAR NOT NULL,
  speed        FLOAT NOT NULL,
  fuel         FLOAT NOT NULL,
  co2          FLOAT NOT NULL,
  cost         UINTEGER NOT NULL,
  capacity     UINTEGER NOT NULL,
  rwy          USMALLINT NOT NULL,
  check_cost   UINTEGER NOT NULL,
  range        USMALLINT NOT NULL,
  ceil         USMALLINT NOT NULL,
  maint        USMALLINT NOT NULL,
  pilots       UTINYINT NOT NULL,
  crew         UTINYINT NOT NULL,
  engineers    UTINYINT NOT NULL,
  technicians  UTINYINT NOT NULL,
  img          VARCHAR NOT NULL,
  wingspan     UTINYINT NOT NULL,
  length       UTINYINT NOT NULL,
);
INSERT INTO aircrafts SELECT * FROM read_parquet('./src/am4utils/data/aircrafts.parquet');
CREATE INDEX aircrafts_idx ON aircrafts(id, name, manufacturer, cargo, eid, ename, speed, fuel, co2, cost, capacity, rwy, check_cost, range, engineers, technicians, img);


CREATE TABLE routes (
  oid USMALLINT NOT NULL,
  did USMALLINT NOT NULL,
  yd  USMALLINT NOT NULL,
  jd  USMALLINT NOT NULL,
  fd  USMALLINT NOT NULL,
  d   FLOAT     NOT NULL,
);
INSERT INTO routes SELECT * FROM read_parquet('./src/am4utils/data/routes.parquet');
CREATE INDEX routes_idx ON routes(oid, did, yd, jd, fd, d);
```