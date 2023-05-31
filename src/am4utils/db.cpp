#include <iostream>
#include <string>
#include <duckdb.hpp>
#include "include/db.hpp"

using namespace std;
using namespace duckdb;

#define VALIDATE(q) if (q->HasError()) { cerr << q->GetError() << endl; return false; }

bool init() {
    Connection con(db);
    
    if (!home_dir.empty()) {
        // WARN: prone to SQLi, duckdb doesn't support prepared statements for config options yet
        auto set_homedir = con.Query("SET home_directory = '" + home_dir + "';");
        VALIDATE(set_homedir);
    }
    
    auto ct_airports = con.Query(
        "CREATE TABLE airports ("
        "  id         USMALLINT PRIMARY KEY NOT NULL,"
        "  name       VARCHAR NOT NULL,"
        "  fullname   VARCHAR NOT NULL,"
        "  country    VARCHAR NOT NULL,"
        "  continent  VARCHAR NOT NULL,"
        "  iata       VARCHAR UNIQUE NOT NULL,"
        "  icao       VARCHAR UNIQUE NOT NULL,"
        "  lat        DOUBLE NOT NULL,"
        "  lng        DOUBLE NOT NULL,"
        "  rwy        USMALLINT NOT NULL,"
        "  market     UTINYINT NOT NULL,"
        "  hub_cost   UINTEGER NOT NULL,"
        "  rwy_codes  VARCHAR NOT NULL"
        ");"
    );
    VALIDATE(ct_airports);
    
    auto ins_airports = con.Query("INSERT INTO airports SELECT * FROM read_parquet('~/data/airports.parquet');");
    VALIDATE(ins_airports);

    auto idx_airports = con.Query("CREATE INDEX airports_idx ON airports(name, fullname, country, continent, lat, lng, rwy, market);");
    VALIDATE(idx_airports);

    // id	name	manufacturer	cargo	eid	ename	speed	fuel	co2	cost	capacity	rwy	check_cost	range	ceil	maint	pilots	crew	engines	technicians	img	wingspan	length
    // 1	B747-400	Boeing	FALSE	2	GE CF6-80C2b5F	946.58	21.21	0.18	92136845	416	10250	7140605	14500	40000	330	2	13	4	4	assets/img/aircraft/png/747-8.png	64	70
    // 1	B747-400	Boeing	FALSE	4	PW4056	982.3	22.89	0.18	92136845	416	10250	7140605	14500	40000	330	2	13	4	4	assets/img/aircraft/png/747-8.png	64	70
    // 1	B747-400	Boeing	FALSE	1	PW4062	866.21	20.16	0.18	92136845	416	10250	7140605	14500	40000	330	2	13	4	4	assets/img/aircraft/png/747-8.png	64	70
    // 1	B747-400	Boeing	FALSE	3	RR RB211-524	884.07	20.79	0.18	92136845	416	10250	7140605	14500	40000	330	2	13	4	4	assets/img/aircraft/png/747-8.png	64	70
    // 2	A380-800	Airbus	FALSE	5	GP7270	963.9	22.89	0.16	215629503	600	9680	6468885	14500	40000	450	2	18	6	16	assets/img/aircraft/png/a380.png	79	72
    // 2	A380-800	Airbus	FALSE	6	RR Trent 970	916.65	18.9	0.16	215629503	600	9680	6468885	14500	40000	450	2	18	6	16	assets/img/aircraft/png/a380.png	79	72
    // 2	A380-800	Airbus	FALSE	7	RR Trent 972	1048.95	22.26	0.16	215629503	600	9680	6468885	14500	40000	450	2	18	6	16	assets/img/aircraft/png/a380.png	79	72
    
    // auto ct_aircrafts = con.Query("CREATE TABLE aircrafts AS SELECT * FROM read_parquet('./data/aircrafts.parquet');");
    // if (!ct_aircrafts->HasError()) {
    //     cerr << ct_aircrafts->GetError();
    //     return false;
    // }

    // auto ct_routes = con.Query("CREATE TABLE routes AS SELECT * FROM read_parquet('./data/routes.parquet');");
    // if (!ct_routes->HasError()) {
    //     cerr << ct_routes->GetError();
    //     return false;
    // }

    return true;
}

void _query(string query) {
    Connection con(db);

    auto result = con.Query(query);
    result->Print();
}

Connection _get_connection() {
    return Connection(db);
}