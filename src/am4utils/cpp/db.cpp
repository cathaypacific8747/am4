#include <iostream>
#include <string>
#include <duckdb.hpp>

#include "include/db.hpp"

using namespace duckdb;

shared_ptr<Database> Database::default_client = nullptr;

shared_ptr<Database> Database::Client() {
    if (!default_client) {
        default_client = make_shared<Database>();
        default_client->database = make_uniq<DuckDB>(":memory:");
        default_client->connection = make_uniq<Connection>(*default_client->database);
    }
    return default_client;
}

// sets the home directory and inserts airports, aircrafts
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
}

void Database::populate_cache() {
    auto result = connection->Query("SELECT id, lat, lng, rwy FROM airports;");
    CHECK_SUCCESS(result);
    int i = 0;
    while (auto chunk = result->Fetch()) {
        for (idx_t j = 0; j < chunk->size(); j++, i++) {
            airport_cache[i] = {
                chunk->GetValue(0, j).GetValue<uint16_t>(),
                chunk->GetValue(1, j).GetValue<double>(),
                chunk->GetValue(2, j).GetValue<double>(),
                chunk->GetValue(3, j).GetValue<uint16_t>()
            };
        }
    }

    result = connection->Query("SELECT yd, jd, fd, d FROM read_parquet('~/data/routes.parquet');");
    CHECK_SUCCESS(result);
    i = 0;
    while (auto chunk = result->Fetch()) {
        for (idx_t j = 0; j < chunk->size(); j++, i++) {
            route_cache[i] = {
                chunk->GetValue(0, j).GetValue<uint16_t>(),
                chunk->GetValue(1, j).GetValue<uint16_t>(),
                chunk->GetValue(2, j).GetValue<uint16_t>(),
                chunk->GetValue(3, j).GetValue<double>(),
            };
        }
    }
}

idx_t Database::get_airport_idx_by_id(uint16_t id) {
    // if (id > 3982) return 3906;
    // static const uint16_t breakpoints[] = {
    //     52, 178, 248, 318, 538, 542, 544, 552, 558, 562,
    //     570, 572, 577, 597, 1110, 1130, 1162, 1200, 1249, 1265,
    //     1306, 1309, 1311, 1313, 1326, 1328, 1356, 1358, 1378, 1381,
    //     1388, 1391, 1468, 1481, 1513, 1528, 1532, 1537, 1540, 1541,
    //     1543, 1571, 1592, 1598, 1625, 1683, 1696, 2382, 2400, 2533,
    //     2557, 2559, 2566, 2573, 2577, 2591, 2597, 2610, 2627, 2630,
    //     2646, 2648, 2656, 2660, 2662, 2664, 2665, 2667, 2673, 3053,
    //     3194, 3506, 3508, 3550, 3899, 3982
    // };
    
    // auto it = std::lower_bound(std::begin(breakpoints), std::end(breakpoints), id);
    // return id - (it - std::begin(breakpoints)) - 1;

    if (id < 53) return id - 1;
    if (id < 179) return id - 2;
    if (id < 249) return id - 3;
    if (id < 319) return id - 4;
    if (id < 539) return id - 5;
    if (id < 543) return id - 6;
    if (id < 545) return id - 7;
    if (id < 553) return id - 8;
    if (id < 559) return id - 9;
    if (id < 563) return id - 10;
    if (id < 571) return id - 11;
    if (id < 573) return id - 12;
    if (id < 578) return id - 13;
    if (id < 598) return id - 14;
    if (id < 1111) return id - 15;
    if (id < 1131) return id - 16;
    if (id < 1163) return id - 17;
    if (id < 1201) return id - 18;
    if (id < 1250) return id - 19;
    if (id < 1266) return id - 20;
    if (id < 1307) return id - 21;
    if (id < 1310) return id - 22;
    if (id < 1312) return id - 23;
    if (id < 1314) return id - 24;
    if (id < 1327) return id - 25;
    if (id < 1329) return id - 26;
    if (id < 1357) return id - 27;
    if (id < 1359) return id - 28;
    if (id < 1379) return id - 29;
    if (id < 1382) return id - 30;
    if (id < 1389) return id - 31;
    if (id < 1392) return id - 32;
    if (id < 1469) return id - 33;
    if (id < 1482) return id - 34;
    if (id < 1514) return id - 35;
    if (id < 1529) return id - 36;
    if (id < 1533) return id - 37;
    if (id < 1538) return id - 38;
    if (id < 1541) return id - 39;
    if (id < 1542) return id - 40;
    if (id < 1544) return id - 41;
    if (id < 1572) return id - 42;
    if (id < 1593) return id - 43;
    if (id < 1599) return id - 44;
    if (id < 1626) return id - 45;
    if (id < 1684) return id - 46;
    if (id < 1697) return id - 47;
    if (id < 2383) return id - 48;
    if (id < 2401) return id - 49;
    if (id < 2534) return id - 50;
    if (id < 2558) return id - 51;
    if (id < 2560) return id - 52;
    if (id < 2567) return id - 53;
    if (id < 2574) return id - 54;
    if (id < 2578) return id - 55;
    if (id < 2592) return id - 56;
    if (id < 2598) return id - 57;
    if (id < 2611) return id - 58;
    if (id < 2628) return id - 59;
    if (id < 2631) return id - 60;
    if (id < 2647) return id - 61;
    if (id < 2649) return id - 62;
    if (id < 2657) return id - 63;
    if (id < 2661) return id - 64;
    if (id < 2663) return id - 65;
    if (id < 2665) return id - 66;
    if (id < 2666) return id - 67;
    if (id < 2668) return id - 68;
    if (id < 2674) return id - 69;
    if (id < 3054) return id - 70;
    if (id < 3195) return id - 71;
    if (id < 3507) return id - 72;
    if (id < 3509) return id - 73;
    if (id < 3551) return id - 74;
    if (id < 3900) return id - 75;
    if (id < 3983) return id - 76;
    return 3907;
}

idx_t Database::get_routecache_idx(idx_t oidx, idx_t didx) {
    if (oidx > didx) {
        return didx * (AIRPORT_COUNT - 1) - (didx * (didx + 1)) / 2 + oidx - 1;
    }
    return oidx * (AIRPORT_COUNT - 1) - (oidx * (oidx + 1)) / 2 + didx - 1;
}

idx_t Database::get_routecache_idx_by_ids(uint16_t oid, uint16_t did) {
    uint16_t i = get_airport_idx_by_id(oid);
    uint16_t j = get_airport_idx_by_id(did);
    return get_routecache_idx(i, j);
}

Database::RouteCache Database::get_route_by_ids(uint16_t oid, uint16_t did) {
    return route_cache[Database::get_routecache_idx_by_ids(oid, did)];
}

void Database::_debug() {

}

void init(string home_dir) {
    auto client = Database::Client();
    client->insert(home_dir);
    client->prepare_statements();
    client->populate_cache();
}

void _debug_query(string query) {
    auto client = Database::Client();

    auto result = client->connection->Query(query);
    result->Print();
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

void pybind_init_db(py::module_& m) {
    py::module_ m_db = m.def_submodule("db");

    m_db
        .def("init", [](std::optional<string> home_dir) {
            if (!home_dir.has_value()) {
                py::gil_scoped_acquire acquire;
                init(py::module::import("am4utils").attr("__path__").cast<py::list>()[0].cast<string>()); // am4utils.__path__[0]
            } else {
                init(home_dir.value());
            }
        }, "home_dir"_a = py::none())
        .def("_debug_query", &_debug_query, "query"_a);

    py::register_exception<DatabaseException>(m_db, "DatabaseException");
}
#endif