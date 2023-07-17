#include <duckdb.hpp>
#include <vector>
#include "airport.hpp"
#include "aircraft.hpp"

constexpr int AIRCRAFT_COUNT = 487;
constexpr int AIRPORT_COUNT = 3907;
constexpr int ROUTE_COUNT = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;

using std::string;
using std::shared_ptr;
using duckdb::DuckDB;
using duckdb::Connection;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)
#define CHECK_SUCCESS(q) if (q->HasError()) throw DatabaseException(q->GetError());
#define CHECK_SUCCESS_REF(q) if (q.HasError()) throw DatabaseException(q.GetError());

// multiple threads can use the same connection?
// https://github.com/duckdb/duckdb/blob/8c32403411d628a400cc32e5fe73df87eb5aad7d/test/api/test_api.cpp#L142
struct Database {
    duckdb::unique_ptr<DuckDB> database;
    duckdb::unique_ptr<Connection> connection;
    
    Airport airports[AIRPORT_COUNT]; // 1,031,448 B
    static idx_t get_airport_idx_by_id(uint16_t id);
    Airport get_airport_by_id(uint16_t id);
    Airport get_airport_by_iata(const string& iata);
    Airport get_airport_by_icao(const string& icao);
    Airport get_airport_by_name(const string& name);
    Airport get_airport_by_all(const string& all);
    std::vector<Airport::Suggestion> suggest_airport_by_iata(const string& iata);
    std::vector<Airport::Suggestion> suggest_airport_by_icao(const string& icao);
    std::vector<Airport::Suggestion> suggest_airport_by_name(const string& name);
    std::vector<Airport::Suggestion> suggest_airport_by_all(const string& all);

    Aircraft aircrafts[AIRCRAFT_COUNT];
    static idx_t get_aircraft_idx_by_id(uint16_t id, uint8_t priority = 0);
    Aircraft get_aircraft_by_id(uint16_t id, uint8_t priority);
    Aircraft get_aircraft_by_shortname(const string& shortname, uint8_t priority);
    Aircraft get_aircraft_by_name(const string& name, uint8_t priority);
    Aircraft get_aircraft_by_all(const string& all, uint8_t priority);
    std::vector<Aircraft::Suggestion> suggest_aircraft_by_shortname(const string& shortname);
    std::vector<Aircraft::Suggestion> suggest_aircraft_by_name(const string& name);
    std::vector<Aircraft::Suggestion> suggest_aircraft_by_all(const string& all);

    struct DBRoute {
        uint16_t yd;
        uint16_t jd;
        uint16_t fd;
        double distance;
    };
    DBRoute routes[ROUTE_COUNT]; // 91,564,452 B
    static idx_t get_dbroute_idx(idx_t oidx, idx_t didx);
    idx_t get_dbroute_idx_by_ids(uint16_t oid, uint16_t did);
    DBRoute get_dbroute_by_ids(uint16_t oid, uint16_t did);
    
    static shared_ptr<Database> default_client;
    static shared_ptr<Database> Client();

    void populate_data(const string& home_dir);
};

struct CompareSuggestion {
    bool operator()(const Airport::Suggestion& s1, const Airport::Suggestion& s2) {
        return s1.score > s2.score;
    }
    bool operator()(const Aircraft::Suggestion& s1, const Aircraft::Suggestion& s2) {
        return s1.score > s2.score;
    }
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