#pragma once
#include <duckdb.hpp>
#include <limits>

#include "game.hpp"
#include "ticket.hpp"
#include "demand.hpp"
#include "airport.hpp"
#include "aircraft.hpp"
#define INF std::numeric_limits<double>::infinity()

using std::string;
using std::to_string;
using std::vector;
// using std::shared_ptr;

constexpr double PI = 3.14159265358979323846;
constexpr double MAX_DISTANCE = 6371 * PI;

struct AircraftRoute;

struct Route {
    PaxDemand pax_demand;
    double direct_distance;
    bool valid;
    
    Route();
    static Route create(const Airport& a0, const Airport& a1);
    
    static inline double calc_distance(double lat1, double lon1, double lat2, double lon2);
    static inline double calc_distance(const Airport& a0, const Airport& a1);
    static const string repr(const Route& r);
};

struct AircraftRoute {
    struct Options {
        uint16_t trips_per_day;
        double max_distance;
        double max_flight_time;

        Options(uint16_t trips_per_day = 1, double max_distance = INF, double max_flight_time = INF);
    };
    Route route;
    Aircraft::Type _ac_type;
    Aircraft::Config config;
    Ticket ticket;
    double max_income;
    double income;
    double fuel;
    double co2;
    double acheck_cost;
    double repair_cost;
    double profit;
    double flight_time;
    bool needs_stopover;
    struct Stopover {
        Airport airport;
        double full_distance;
        bool exists;

        Stopover();
        Stopover(const Airport& airport, double full_distance);
        static Stopover find_by_efficiency(const Airport& origin, const Airport& destination, const Aircraft& aircraft, User::GameMode game_mode);
        // static Stopover find_by_target_distance(const Airport& origin, const Airport& destination, const Aircraft& aircraft, double target_distance, User::GameMode game_mode);
        const static string repr(const Stopover& s);
    };

    Stopover stopover;
    enum class Warning {
        ERR_DISTANCE_ABOVE_SPECIFIED,
        ERR_DISTANCE_TOO_LONG,
        ERR_DISTANCE_TOO_SHORT,
        REDUCED_CONTRIBUTION,
        ERR_NO_STOPOVER,
        ERR_FLIGHT_TIME_ABOVE_SPECIFIED,
        ERR_INSUFFICIENT_DEMAND
    };
    vector<Warning> warnings;
    bool valid;

    AircraftRoute();
    static AircraftRoute create(const Airport& a0, const Airport& a1, const Aircraft& ac, const Options& options = Options(), const User& user = User::Default());
    
    static inline double estimate_load(double reputation = 87, double autoprice_ratio = 1.06, bool has_stopover = false); // 1.06 just to trigger the autoprice branch
    static inline double calc_fuel(const Aircraft& ac, double distance, const User& user = User::Default(), uint8_t ci = 200);
    static inline double calc_co2(const Aircraft& ac, const Aircraft::Config& cfg, double distance, double load, const User& user = User::Default(), uint8_t ci = 200);
    static const string repr(const AircraftRoute& acr);
};

struct Destination {
    Airport airport;
    AircraftRoute ac_route;

    Destination(const Airport& destination, const AircraftRoute& route);
};

vector<Destination> find_routes(const Airport& origin, const Aircraft& aircraft, const AircraftRoute::Options& options = AircraftRoute::Options(), const User& user = User::Default());