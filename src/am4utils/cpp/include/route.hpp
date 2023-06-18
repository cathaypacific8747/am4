#pragma once
#include <duckdb.hpp>

#include "game.hpp"
#include "ticket.hpp"
#include "demand.hpp"

#include "airport.hpp"
#include "aircraft.hpp"

using std::string;
using std::to_string;
using std::vector;

struct AircraftRoute;

struct Route {
    Airport origin;
    Airport destination;
    PaxDemand pax_demand;
    double direct_distance;
    bool valid;
    
    Route();
    static Route create(const Airport& a0, const Airport& a1);
    AircraftRoute assign(const Aircraft& ac, uint16_t trips_per_day = 1, const User& user = User());
    
    static inline duckdb::unique_ptr<duckdb::QueryResult> _get_route_result(uint16_t id0, uint16_t id1);
    static inline double calc_distance(double lat1, double lon1, double lat2, double lon2);
    static inline double calc_distance(const Airport& a0, const Airport& a1);
    static const string repr(const Route& r);
};

struct AircraftRoute {
    Route route;
    PurchasedAircraft aircraft;
    Ticket ticket;
    double income;
    bool needs_stopover;
    bool valid;
    // vector<string> warnings;

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

    AircraftRoute();
    static AircraftRoute from(const Route& r, const Aircraft& ac, uint16_t trips_per_day = 1, const User& user = User());
    
    static inline double estimate_load(uint8_t reputation, double autoprice_ratio, bool has_stopover = false);
    static const string repr(const AircraftRoute& acr);
};