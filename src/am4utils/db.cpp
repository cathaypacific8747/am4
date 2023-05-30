#include <iostream>
#include <string>
#include <duckdb.hpp>
#include "include/db.hpp"

using namespace std;
using namespace duckdb;

bool init_db() {
    Connection con(db);
    
    if (home_dir != "") {
        // WARN: prone to SQLi, duckdb doesn't support prepared statements for config options yet
        con.Query("SET home_directory = '" + home_dir + "';");
    }

    auto ct_airports = con.Query("CREATE TABLE airports AS SELECT * FROM read_parquet('~/data/airports.parquet');");
    if (!ct_airports->HasError()) {
        cerr << ct_airports->GetError();
        return false;
    }

    auto ct_routes = con.Query("CREATE TABLE routes AS SELECT * FROM read_parquet('~/data/routes.parquet');");
    if (!ct_routes->HasError()) {
        cerr << ct_routes->GetError();
        return false;
    }

    return true;
}

void query_db(string query) {
    Connection con(db);

    auto result = con.Query(query);
    result->Print();
}