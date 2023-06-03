#include <iostream>
#include <string>
#include <duckdb.hpp>
#include "include/db.hpp"

using namespace std;
using namespace duckdb;

shared_ptr<Database> Database::default_client = nullptr;
shared_ptr<Database> Database::CreateClient() {
    shared_ptr<Database> client = make_shared<Database>();
    client->database = make_uniq<DuckDB>(nullptr);
    client->connection = make_uniq<Connection>(*client->database);
    cout << "default_client initialized" << endl;

    return client;
}

shared_ptr<Database> Database::Client() {
	if (!default_client) {
		default_client = Database::CreateClient();
	}
	return default_client;
}

// sets the home directory and inserts airports, aircrafts and routes
void Database::prepare_db() {
    if (!home_dir.empty()) {
        CHECK_SUCCESS(connection->Query("SET home_directory = '" + home_dir + "';"));
    }

    // airports
    CHECK_SUCCESS(connection->Query(
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
    ));
    CHECK_SUCCESS(connection->Query("INSERT INTO airports SELECT * FROM read_parquet('~/data/airports.parquet');"));
    CHECK_SUCCESS(connection->Query("CREATE INDEX airports_idx ON airports(name, fullname, country, continent, lat, lng, rwy, market);"));

    // aircrafts
    CHECK_SUCCESS(connection->Query(
        "CREATE TABLE aircrafts ("
        "  id           USMALLINT NOT NULL,"
        "  shortname    VARCHAR NOT NULL,"
        "  manufacturer VARCHAR NOT NULL,"
        "  name         VARCHAR NOT NULL,"
        "  type         UTINYINT NOT NULL,"
        "  priority     UTINYINT NOT NULL,"
        "  eid          USMALLINT NOT NULL,"
        "  ename        VARCHAR NOT NULL,"
        "  speed        FLOAT NOT NULL,"
        "  fuel         FLOAT NOT NULL,"
        "  co2          FLOAT NOT NULL,"
        "  cost         UINTEGER NOT NULL,"
        "  capacity     UINTEGER NOT NULL,"
        "  rwy          USMALLINT NOT NULL,"
        "  check_cost   UINTEGER NOT NULL,"
        "  range        USMALLINT NOT NULL,"
        "  ceil         USMALLINT NOT NULL,"
        "  maint        USMALLINT NOT NULL,"
        "  pilots       UTINYINT NOT NULL,"
        "  crew         UTINYINT NOT NULL,"
        "  engineers    UTINYINT NOT NULL,"
        "  technicians  UTINYINT NOT NULL,"
        "  img          VARCHAR NOT NULL,"
        "  wingspan     UTINYINT NOT NULL,"
        "  length       UTINYINT NOT NULL,"
        ");"
    ));
    CHECK_SUCCESS(connection->Query("INSERT INTO aircrafts SELECT * FROM read_parquet('~/data/aircrafts.parquet');"));
    CHECK_SUCCESS(connection->Query("CREATE INDEX aircrafts_idx ON aircrafts(id, shortname, manufacturer, name, type, priority, eid, ename, speed, fuel, co2, cost, capacity, rwy, check_cost, range, maint, img);"));

    CHECK_SUCCESS(connection->Query(
        "CREATE TABLE routes ("
        "  oid USMALLINT NOT NULL,"
        "  did USMALLINT NOT NULL,"
        "  yd  USMALLINT NOT NULL,"
        "  jd  USMALLINT NOT NULL,"
        "  fd  USMALLINT NOT NULL,"
        "  d   FLOAT     NOT NULL,"
        ");"
    ));
    CHECK_SUCCESS(connection->Query("INSERT INTO routes SELECT * FROM read_parquet('~/data/routes.parquet');"));
    CHECK_SUCCESS(connection->Query("CREATE INDEX routes_idx ON routes(oid, did, yd, jd, fd, d);"));
}

void Database::prepare_statements() {
    get_airport_by_id = connection->Prepare("SELECT * FROM airports WHERE id = $1");
    CHECK_SUCCESS(get_airport_by_id);

    get_route_demands_by_id = connection->Prepare("SELECT yd, jd, fd FROM routes WHERE oid = $1 AND did = $2;");
    CHECK_SUCCESS(get_route_demands_by_id);
}

void init() {
    Database::Client()->prepare_db();
    Database::Client()->prepare_statements();
}

void _debug_query(string query) {
    auto client = Database::Client();

    auto result = client->connection->Query(query);
    result->Print();
}