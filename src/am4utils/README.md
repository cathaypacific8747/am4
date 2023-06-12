# am4utils

Tools and utilities for Airline Manager 4 bot.

Supports Python 3.9 - 3.11 on the following platforms:
- manylinux2_24 x86_64 (ubuntu 16.10+, debian 9+, fedora 25+)
- windows amd64
- macos x86_64 / amd64

### Database tests
download the [DuckDB command line binaries](https://duckdb.org/docs/installation/)

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
INSERT INTO airports SELECT * FROM read_parquet('./data/airports.parquet');
CREATE INDEX airports_idx ON airports(name, fullname, country, continent, lat, lng, rwy, market);

SELECT *, jaro_winkler_similarity(name, 'hostomel') AS score FROM airports ORDER BY score DESC LIMIT 5;

CREATE TABLE aircrafts (
  id           USMALLINT NOT NULL,
  shortname    VARCHAR NOT NULL,
  manufacturer VARCHAR NOT NULL,
  name         VARCHAR NOT NULL,
  type         UTINYINT NOT NULL,
  priority     UTINYINT NOT NULL,
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
INSERT INTO aircrafts SELECT * FROM read_parquet('./data/aircrafts.parquet');
CREATE INDEX aircrafts_idx ON aircrafts(id, shortname, manufacturer, name, type, priority, eid, ename, speed, fuel, co2, cost, capacity, rwy, check_cost, range, maint, img);


CREATE TABLE routes (
  oid USMALLINT NOT NULL,
  did USMALLINT NOT NULL,
  yd  USMALLINT NOT NULL,
  jd  USMALLINT NOT NULL,
  fd  USMALLINT NOT NULL,
  d   FLOAT     NOT NULL,
);
INSERT INTO routes SELECT * FROM read_parquet('./data/routes.parquet');
CREATE INDEX routes_idx ON routes(oid, did, yd, jd, fd, d);
```