#pragma once
#include <duckdb.hpp>
#include <vector>
#include "airport.hpp"
#include "aircraft.hpp"

using std::string;
using std::shared_ptr;
using duckdb::DuckDB;
using duckdb::Connection;
using duckdb::QueryResult;
using duckdb::MaterializedQueryResult;
using duckdb::PreparedStatement;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)
#define USER_COLUMNS "id, username, game_id, game_name, game_mode, discord_id, wear_training, repair_training, l_training, h_training, fuel_training, co2_training, fuel_price, co2_price, accumulated_count, load, role"
#define SELECT_USER_STATEMENT(field) "SELECT " USER_COLUMNS " FROM users WHERE " #field " = $1 LIMIT 1;"
#define INSERT_USER_STATEMENT "INSERT INTO users (username, password, game_id, game_name, game_mode, discord_id) VALUES ($1, $2, $3, $4, $5, $6) RETURNING " USER_COLUMNS ";"

constexpr int AIRCRAFT_COUNT = 487;
constexpr int AIRPORT_COUNT = 3907;
constexpr int ROUTE_COUNT = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;

class DatabaseException : public std::exception {
private:
    string msg;
public:
    DatabaseException(string msg) : msg(msg) {}
    const char* what() const throw() { return msg.c_str(); }
};

template <typename T>
inline void CHECK_SUCCESS(duckdb::unique_ptr<T>& q) {
    if (q->HasError()) throw DatabaseException(q->GetError());
}
inline void VERIFY_SUCCESS_AND_SIZE(duckdb::unique_ptr<duckdb::QueryResult>& q, idx_t size) {
    CHECK_SUCCESS(q);
    auto result = q->Fetch();
    if (!result || result->size() != size) throw DatabaseException("result size mismatch!");
}

// multiple threads can use the same connection?
// https://github.com/duckdb/duckdb/blob/8c32403411d628a400cc32e5fe73df87eb5aad7d/test/api/test_api.cpp#L142
struct Database {
    duckdb::unique_ptr<DuckDB> database;
    duckdb::unique_ptr<Connection> connection;
    
    duckdb::unique_ptr<PreparedStatement> insert_user;
    duckdb::unique_ptr<PreparedStatement> get_user_by_id;
    duckdb::unique_ptr<PreparedStatement> get_user_by_username;
    duckdb::unique_ptr<PreparedStatement> get_user_by_discord_id;
    duckdb::unique_ptr<PreparedStatement> get_user_by_game_id;
    duckdb::unique_ptr<PreparedStatement> get_user_by_ign;
    duckdb::unique_ptr<PreparedStatement> update_user_game_mode;

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
    static shared_ptr<Database> Client(const string& home_dir, const string& db_name);

    void populate_database();
    void populate_internal();
};

struct CompareSuggestion {
    bool operator()(const Airport::Suggestion& s1, const Airport::Suggestion& s2) {
        return s1.score > s2.score;
    }
    bool operator()(const Aircraft::Suggestion& s1, const Aircraft::Suggestion& s2) {
        return s1.score > s2.score;
    }
};

void init(string home_dir, string db_name = "main");
void reset();
void _debug_query(string query);