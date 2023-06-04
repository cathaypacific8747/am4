# ![logo](src/am4bot/assets/img/logo-small.png) am4bot

[![](https://dcbadge.vercel.app/api/server/4tVQHtf?style=flat)](https://discord.gg/4tVQHtf)

A discord bot for the game [Airline Manager 4](airlinemanager.com), used on our [server](https://discord.gg/4tVQHtf).

Our bot is currently running legacy code in the [`src-old`](./src-old/) directory: I am currently planning to rewrite the core calculations in [C++](/src/am4utils/binder.cpp) for better performance and the rest in Python. The backend for [am4help.com](https://am4help.com/) is developed in a separate repository and can be found [here](https://github.com/br-tsilva/api.am4tools.com) instead.

## Current Features
- calculates essential statistics
    - most distance-efficient stopovers
    - route demands, best seat configurations, best ticket prices, estimated income
    - player rank, mode, achievements, fleet
    - alliance rank, share value, contribution
    - aircraft characteristics and profit
    - airport characteristics
- CSV export for route queries
- fuel/CO2 notifications
- aircraft characteristics comparisons
- internal *Star Alliance* tools (now disbanded)
    - adding competitor alliances to watchlist
    - alliance comparisons over time: value, contribution/day, rate of changes
    - realtime alliance-member comparisons: SV/contribution distribution
    - member tracking: cheat detection tools, departure pattern identification

## Commands

### Public
- `$route|stop <airport> <airport> <aircraft> [flights_per_day] [reputation]`: finds the best route between two airports
  
  ![route](src/am4bot/assets/img/route.png)
- `$routes <airport> <aircraft> <max_distance> <flights_per_day> [reputation]`: finds the best destinations from a certain airport, sorted by decreasing estimated income
  
  ![routes](src/am4bot/assets/img/routes.png)
- `$user [player]`: shows player (and associated alliance if found) statistics
  
  ![user](src/am4bot/assets/img/user.png)
- `$fleet [player]`: shows player fleet and estimated income
  
  ![fleet](src/am4bot/assets/img/fleet.png)
- `$info <aircraft>`: shows basic aircraft information and rough profit estimations
  
  ![info](src/am4bot/assets/img/info.png)
- `$compare <aircraft>`: compares two aircrafts
  
  ![compare](src/am4bot/assets/img/compare.png)
- `$search <aircraft>`: finds the associated aircraft shortname for aircraft commands
  
  ![search](src/am4bot/assets/img/search.png)
- `$airport <airport>`: shows airport information
  
  ![airport](src/am4bot/assets/img/airport.png)
- `$price f[fuel_price] c[co2_price]`: notifies everyone for the fuel price
  
  ![price](src/am4bot/assets/img/price.png)

### Internal Alliance Tools
- `$memberCompare <player> <player>`: compares descending structure of contribution/day and SV
  
  ![member-compare](src/am4bot/assets/img/member-compare.png)
- `$alliance <alliance>`: shows AV progression and d(AV)/dt.
  
  ![alliance](src/am4bot/assets/img/alliance.png)
- `$allianceCompare <alliance> <alliance>`: compares AV progression and gap difference over time, shows 48h/12h-average contribution/day graphs
  
  ![alliance-compare](src/am4bot/assets/img/alliance-compare.png)
- `$member <player> [player[]]` shows contribution/day, total contribution and SV history for 1+ members
  
  ![member](src/am4bot/assets/img/member.png)
- `$actions <player> [maxResults]`: shows log of estimated departures, contributions and income
  
  ![member-compare](src/am4bot/assets/img/member-compare.png)
- `$watchlist [add|+, remove|rm|-] [alliance]`: shows, adds or remove alliance(s) to the watchlist


## Development for rewrite
Requirements: python3.11

```bash
# windows
virtualenv .venv
.venv\Scripts\activate

# linux
sudo apt install build-essential
virtualenv .venv
source .venv/bin/activate

###
pip3 uninstall am4utils -y && pip3 install --verbose ".[dev]"
pytest

mkdir build
cd build
cmake .. && cmake --build . && ./_core_executable

.venv/scripts/deactivate
```

### database tests
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
INSERT INTO airports SELECT * FROM read_parquet('./src/am4utils/data/airports.parquet');
CREATE INDEX airports_idx ON airports(name, fullname, country, continent, lat, lng, rwy, market);

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
INSERT INTO aircrafts SELECT * FROM read_parquet('./src/am4utils/data/aircrafts.parquet');
CREATE INDEX aircrafts_idx ON aircrafts(id, shortname, manufacturer, name, type, priority, eid, ename, speed, fuel, co2, cost, capacity, rwy, check_cost, range, maint, img);


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