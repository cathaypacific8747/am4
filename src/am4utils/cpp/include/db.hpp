#include <duckdb.hpp>
#include <vector>
// #include "airport.hpp"

#define AIRPORT_COUNT 3907
#define ROUTE_COUNT AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2

using std::string;
using std::shared_ptr;
using duckdb::DuckDB;
using duckdb::Connection;
using duckdb::PreparedStatement;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)
#define CHECK_SUCCESS(q) if (q->HasError()) throw DatabaseException(q->GetError());
#define CHECK_SUCCESS_REF(q) if (q.HasError()) throw DatabaseException(q.GetError());

// multiple threads can use the same connection?
// https://github.com/duckdb/duckdb/blob/8c32403411d628a400cc32e5fe73df87eb5aad7d/test/api/test_api.cpp#L142
struct Database {
    duckdb::unique_ptr<DuckDB> database;
    duckdb::unique_ptr<Connection> connection;
    
    duckdb::unique_ptr<PreparedStatement> get_airport_by_id;
    duckdb::unique_ptr<PreparedStatement> get_airport_by_iata;
    duckdb::unique_ptr<PreparedStatement> get_airport_by_icao;
    duckdb::unique_ptr<PreparedStatement> get_airport_by_name;
    duckdb::unique_ptr<PreparedStatement> get_airport_by_all;
    duckdb::unique_ptr<PreparedStatement> suggest_airport_by_iata;
    duckdb::unique_ptr<PreparedStatement> suggest_airport_by_icao;
    duckdb::unique_ptr<PreparedStatement> suggest_airport_by_name;

    duckdb::unique_ptr<PreparedStatement> get_aircraft_by_id;
    duckdb::unique_ptr<PreparedStatement> get_aircraft_by_shortname;
    duckdb::unique_ptr<PreparedStatement> get_aircraft_by_name;
    duckdb::unique_ptr<PreparedStatement> get_aircraft_by_all;
    duckdb::unique_ptr<PreparedStatement> suggest_aircraft_by_shortname;
    duckdb::unique_ptr<PreparedStatement> suggest_aircraft_by_name;

    struct AirportCache {
        uint16_t id;
        double lat;
        double lng;
        uint16_t rwy;
    };
    AirportCache airport_cache[AIRPORT_COUNT]; // 125,024 B, for stopovers
    // Airport full_airport_cache[AIRPORT_COUNT];
    static idx_t get_airport_idx_by_id(uint16_t id);

    struct RouteCache {
        uint16_t yd;
        uint16_t jd;
        uint16_t fd;
        double distance;
    };
    RouteCache route_cache[ROUTE_COUNT]; // 91,564,452 B
    static idx_t get_routecache_idx(idx_t oidx, idx_t didx);
    idx_t get_routecache_idx_by_ids(uint16_t oid, uint16_t did);
    RouteCache get_route_by_ids(uint16_t oid, uint16_t did);
    
    static shared_ptr<Database> default_client;
    static shared_ptr<Database> Client();

    void insert(string home_dir);
    void prepare_statements();
    void populate_cache();

    void _debug();
};

void init(string home_dir);
void _debug_query(string query);

class DatabaseException : public std::exception {
private:
    string msg;
public:
    DatabaseException(string msg) : msg(msg) {}
    const char* what() const throw() { return msg.c_str(); }
};