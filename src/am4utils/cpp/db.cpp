#include <iostream>
#include <string>
#include <duckdb.hpp>

#include "include/db.hpp"

using std::string;
using namespace duckdb;

shared_ptr<Database> Database::default_client = nullptr;
shared_ptr<Database> Database::CreateClient() {
    shared_ptr<Database> client = make_shared<Database>();
    client->database = make_uniq<DuckDB>(nullptr);
    client->connection = make_uniq<Connection>(*client->database);

    return client;
}

shared_ptr<Database> Database::Client() {
	if (!default_client) {
		default_client = Database::CreateClient();
	}
	return default_client;
}

// sets the home directory and inserts airports, aircrafts and routes
void Database::insert(string home_dir) {
    CHECK_SUCCESS(connection->Query("SET home_directory = '" + home_dir + "';"));

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
    get_airport_by_id = connection->Prepare("SELECT * FROM airports WHERE id = $1 LIMIT 1");
    CHECK_SUCCESS(get_airport_by_id);

    get_airport_by_iata = connection->Prepare("SELECT * FROM airports WHERE iata = $1 LIMIT 1"); // $1: expects uppercase
    CHECK_SUCCESS(get_airport_by_iata);

    get_airport_by_icao = connection->Prepare("SELECT * FROM airports WHERE icao = $1 LIMIT 1"); // $1: expects uppercase
    CHECK_SUCCESS(get_airport_by_icao);

    get_airport_by_name = connection->Prepare("SELECT * FROM airports WHERE upper(name) = $1 LIMIT 1");
    CHECK_SUCCESS(get_airport_by_name);

    get_airport_by_all = connection->Prepare("SELECT * FROM airports WHERE iata = $1 OR icao = $1 OR upper(name) = $1 LIMIT 1");
    CHECK_SUCCESS(get_airport_by_all);

    suggest_airport_by_iata = connection->Prepare("SELECT *, jaro_winkler_similarity(iata, $1) AS score FROM airports ORDER BY score DESC LIMIT 5");
    CHECK_SUCCESS(suggest_airport_by_iata);

    suggest_airport_by_icao = connection->Prepare("SELECT *, jaro_winkler_similarity(icao, $1) AS score FROM airports ORDER BY score DESC LIMIT 5");
    CHECK_SUCCESS(suggest_airport_by_icao);

    suggest_airport_by_name = connection->Prepare("SELECT *, jaro_winkler_similarity(upper(name), $1) AS score FROM airports ORDER BY score DESC LIMIT 5");
    CHECK_SUCCESS(suggest_airport_by_name);


    get_aircraft_by_id = connection->Prepare("SELECT * FROM aircrafts WHERE id = $1 AND priority = $2 LIMIT 1");
    CHECK_SUCCESS(get_aircraft_by_id);

    get_aircraft_by_shortname = connection->Prepare("SELECT * FROM aircrafts WHERE shortname = $1 AND priority = $2 LIMIT 1"); // $1: expects lowercase
    CHECK_SUCCESS(get_aircraft_by_shortname);

    get_aircraft_by_name = connection->Prepare("SELECT * FROM aircrafts WHERE lower(name) = $1 AND priority = $2 LIMIT 1");
    CHECK_SUCCESS(get_aircraft_by_name);

    get_aircraft_by_all = connection->Prepare("SELECT * FROM aircrafts WHERE (shortname = $1 OR lower(name) = $1) AND priority = $2 LIMIT 1");
    CHECK_SUCCESS(get_aircraft_by_all);

    suggest_aircraft_by_shortname = connection->Prepare("SELECT *, jaro_winkler_similarity(shortname, $1) AS score FROM aircrafts WHERE priority = $2 ORDER BY score DESC LIMIT 5");
    CHECK_SUCCESS(suggest_aircraft_by_shortname);

    suggest_aircraft_by_name = connection->Prepare("SELECT *, jaro_winkler_similarity(lower(name), $1) AS score FROM aircrafts WHERE priority = $2 ORDER BY score DESC LIMIT 5");
    CHECK_SUCCESS(suggest_aircraft_by_name);


    get_route_demands_by_id = connection->Prepare("SELECT yd, jd, fd FROM routes WHERE oid = $1 AND did = $2;");
    CHECK_SUCCESS(get_route_demands_by_id);
}

void init(string home_dir) {
    Database::Client()->insert(home_dir);
    Database::Client()->prepare_statements();
}

void _debug_query(string query) {
    auto client = Database::Client();

    auto result = client->connection->Query(query);
    result->Print();
}