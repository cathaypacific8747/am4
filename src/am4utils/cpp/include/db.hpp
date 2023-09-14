#pragma once
#include <duckdb.hpp>
#include <vector>
#include "airport.hpp"
#include "aircraft.hpp"

using std::string;
using std::shared_ptr;
using duckdb::DuckDB;
using duckdb::Connection;
using duckdb::PreparedStatement;
using duckdb::Appender;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

constexpr int AIRCRAFT_COUNT = 487;
constexpr int AIRPORT_COUNT = 3907;
constexpr int AIRPORT_ID_MAX = 3982;
constexpr int ROUTE_COUNT = AIRPORT_COUNT * (AIRPORT_COUNT - 1) / 2;

class DatabaseException : public std::exception {
private:
    string msg;
public:
    DatabaseException(string msg) : msg(msg) {}
    const char* what() const throw() { return msg.c_str(); }
};

template <typename T>
inline void CHECK_SUCCESS(duckdb::unique_ptr<T> q) {
    if (q->HasError()) throw DatabaseException(q->GetError());
}
template <typename T>
inline void CHECK_SUCCESS_REF(duckdb::unique_ptr<T>& q) {
    if (q->HasError()) throw DatabaseException(q->GetError());
}
template <typename T>
inline void VERIFY_UPDATE_SUCCESS(duckdb::unique_ptr<T> q) {
    CHECK_SUCCESS_REF(q);
    auto result = q->Fetch();
    if (!result || result->size() != 1) throw DatabaseException("FATAL: cannot update user!");
}

// multiple threads can use the same connection?
// https://github.com/duckdb/duckdb/blob/8c32403411d628a400cc32e5fe73df87eb5aad7d/test/api/test_api.cpp#L142
struct Database {
    duckdb::unique_ptr<DuckDB> database;
    duckdb::unique_ptr<Connection> connection;
    
    duckdb::unique_ptr<PreparedStatement> verify_user_by_username;
    duckdb::unique_ptr<PreparedStatement> insert_user;
    duckdb::unique_ptr<PreparedStatement> get_user_by_id;
    duckdb::unique_ptr<PreparedStatement> get_user_by_username;
    duckdb::unique_ptr<PreparedStatement> get_user_by_game_id;
    duckdb::unique_ptr<PreparedStatement> get_user_by_game_name;
    duckdb::unique_ptr<PreparedStatement> get_user_by_discord_id;
    
    duckdb::unique_ptr<PreparedStatement> get_user_password;

    duckdb::unique_ptr<PreparedStatement> update_user_username;
    duckdb::unique_ptr<PreparedStatement> update_user_password;
    duckdb::unique_ptr<PreparedStatement> update_user_game_id;
    duckdb::unique_ptr<PreparedStatement> update_user_game_name;
    duckdb::unique_ptr<PreparedStatement> update_user_game_mode;
    duckdb::unique_ptr<PreparedStatement> update_user_discord_id;
    duckdb::unique_ptr<PreparedStatement> update_user_wear_training;
    duckdb::unique_ptr<PreparedStatement> update_user_repair_training;
    duckdb::unique_ptr<PreparedStatement> update_user_l_training;
    duckdb::unique_ptr<PreparedStatement> update_user_h_training;
    duckdb::unique_ptr<PreparedStatement> update_user_fuel_training;
    duckdb::unique_ptr<PreparedStatement> update_user_co2_training;
    duckdb::unique_ptr<PreparedStatement> update_user_fuel_price;
    duckdb::unique_ptr<PreparedStatement> update_user_co2_price;
    duckdb::unique_ptr<PreparedStatement> update_user_accumulated_count;
    duckdb::unique_ptr<PreparedStatement> update_user_load;
    duckdb::unique_ptr<PreparedStatement> update_user_income_loss_tol;
    duckdb::unique_ptr<PreparedStatement> update_user_fourx;
    duckdb::unique_ptr<PreparedStatement> update_user_role;

    duckdb::unique_ptr<PreparedStatement> get_alliance_log_by_log_id;

    Airport airports[AIRPORT_COUNT]; // 1,031,448 B
    uint16_t airport_id_hashtable[AIRPORT_ID_MAX + 1]; // 63,728 B: airport id -> airports index
    Airport get_airport_by_id(uint16_t id);
    // note: input string are assumed to be already uppercased
    Airport get_airport_by_iata(const string& iata);
    Airport get_airport_by_icao(const string& icao);
    Airport get_airport_by_name(const string& name);
    Airport get_airport_by_fullname(const string& name);
    Airport get_airport_by_all(const string& all);
    
    template<typename ScoreFn>
    std::vector<Airport::Suggestion> suggest_airport(const string& input, ScoreFn score_fn);
    std::vector<Airport::Suggestion> suggest_airport_by_iata(const string& iata);
    std::vector<Airport::Suggestion> suggest_airport_by_icao(const string& icao);
    std::vector<Airport::Suggestion> suggest_airport_by_name(const string& name);
    std::vector<Airport::Suggestion> suggest_airport_by_fullname(const string& name);
    std::vector<Airport::Suggestion> suggest_airport_by_all(const string& all);

    Aircraft aircrafts[AIRCRAFT_COUNT];
    static uint16_t get_aircraft_idx_by_id(uint16_t id, uint8_t priority = 0);
    // note: input string are assumed to be already lowercased
    Aircraft get_aircraft_by_id(uint16_t id, uint8_t priority);
    Aircraft get_aircraft_by_shortname(const string& shortname, uint8_t priority);
    Aircraft get_aircraft_by_name(const string& name, uint8_t priority);
    Aircraft get_aircraft_by_all(const string& all, uint8_t priority);
    
    template<typename ScoreFn>
    std::vector<Aircraft::Suggestion> suggest_aircraft(const string& input, ScoreFn score_fn);
    std::vector<Aircraft::Suggestion> suggest_aircraft_by_shortname(const string& shortname);
    std::vector<Aircraft::Suggestion> suggest_aircraft_by_name(const string& name);
    std::vector<Aircraft::Suggestion> suggest_aircraft_by_all(const string& all);

    PaxDemand pax_demands[ROUTE_COUNT];
    double distances[AIRPORT_COUNT][AIRPORT_COUNT]; // 96,799,832 B
    static inline uint32_t get_dbroute_idx(uint16_t oidx, uint16_t didx) {
        if (oidx > didx)
            return ((didx * (2*AIRPORT_COUNT - didx - 1)) >> 1) + oidx - didx - 1;
        return ((oidx * (2*AIRPORT_COUNT - oidx - 1)) >> 1) + didx - oidx - 1;
    };
    
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