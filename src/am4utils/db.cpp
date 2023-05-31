#include <iostream>
#include <string>
#include <duckdb.hpp>
#include "include/db.hpp"

using namespace std;
using namespace duckdb;

#define VALIDATE(q) if (q->HasError()) { cerr << q->GetError() << endl; return false; }

// adapted from: duckdb/tools/pythonpkg/src/pyconnection.cpp
shared_ptr<DatabaseConnection> DatabaseConnection::default_connection = nullptr;
shared_ptr<DatabaseConnection> DatabaseConnection::CreateNewInstance() {
    auto con = make_shared<DatabaseConnection>();
    con->database = make_uniq<DuckDB>(":memory:");
    con->connection = make_uniq<Connection>(*con->database);
    // cout << "default_connection initialized" << endl;

    return con;
}

shared_ptr<DatabaseConnection> DatabaseConnection::DefaultConnection() {
	if (!default_connection) {
		default_connection = DatabaseConnection::CreateNewInstance();
	}
	return default_connection;
}

shared_ptr<DatabaseConnection> DatabaseConnection::Clone() {
    if (!connection) {
        cerr << "connection is null, cannot clone." << endl;
        return nullptr;
    }
    auto con = make_shared<DatabaseConnection>();
    con->database = this->database;
    con->connection = make_uniq<Connection>(*con->database);

    connections.push_back(con);
    return con;
}

void DatabaseConnection::CloseAll() {
    connection = nullptr;
    database = nullptr;
    for (auto &con : connections) {
        con->CloseAll();
    }
}

// sets the home directory and inserts airports, aircrafts and routes
bool DatabaseConnection::prepare_db() {
    if (!home_dir.empty()) {
        // WARN: prone to SQLi, duckdb doesn't support prepared statements for config options yet
        auto set_homedir = connection->Query("SET home_directory = '" + home_dir + "';");
        VALIDATE(set_homedir);
    }

    auto ct_airports = connection->Query(
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
    
    auto ins_airports = connection->Query("INSERT INTO airports SELECT * FROM read_parquet('~/data/airports.parquet');");
    VALIDATE(ins_airports);

    auto idx_airports = connection->Query("CREATE INDEX airports_idx ON airports(name, fullname, country, continent, lat, lng, rwy, market);");
    VALIDATE(idx_airports);

    auto ct_aircrafts = connection->Query(
        "CREATE TABLE aircrafts ("
        "  id           USMALLINT NOT NULL,"
        "  name         VARCHAR NOT NULL,"
        "  manufacturer VARCHAR NOT NULL,"
        "  cargo        BOOLEAN NOT NULL,"
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
    );
    VALIDATE(ct_aircrafts);

    auto ins_aircrafts = connection->Query("INSERT INTO aircrafts SELECT * FROM read_parquet('~/data/aircrafts.parquet');");
    VALIDATE(ins_aircrafts);

    auto idx_aircrafts = connection->Query("CREATE INDEX aircrafts_idx ON aircrafts(id, name, manufacturer, cargo, eid, ename, speed, fuel, co2, cost, capacity, rwy, check_cost, range, engineers, technicians, img);");
    VALIDATE(idx_aircrafts);

    auto insert_routes = connection->Query(
        "CREATE TABLE routes ("
        "  oid USMALLINT NOT NULL,"
        "  did USMALLINT NOT NULL,"
        "  yd  USMALLINT NOT NULL,"
        "  jd  USMALLINT NOT NULL,"
        "  fd  USMALLINT NOT NULL,"
        "  d   FLOAT     NOT NULL,"
        ");"
    );
    VALIDATE(insert_routes);

    auto ins_routes = connection->Query("INSERT INTO routes SELECT * FROM read_parquet('~/data/routes.parquet');");
    VALIDATE(ins_routes);

    auto idx_routes = connection->Query("CREATE INDEX routes_idx ON routes(oid, did, yd, jd, fd, d);");
    VALIDATE(idx_routes);

    return true;
}

bool init() {
    return DatabaseConnection::DefaultConnection()->prepare_db();
}

void _debug_query(string query) {
    auto con = DatabaseConnection::DefaultConnection()->Clone();

    auto result = con->connection->Query(query);
    result->Print();
}