#pragma once
#include <duckdb.hpp>

#include "user.hpp"
#include "ticket.hpp"
#include "demand.hpp"

#include "airport.hpp"
#include "aircraft.hpp"

constexpr double PI = 3.14159265358979323846;

struct Route {
    Airport origin;
    // Airport stopover;
    Airport destination;

    PaxDemand pax_demand;
    CargoDemand cargo_demand;

    PurchasedAircraft aircraft;
    Ticket ticket;
    uint32_t income;

    double direct_distance;
    bool valid = false;
    // bool has_stopover = false;
    // double stopover_extra_distance = 0.0;

    Route();
    static Route from_airports(const Airport& a0, const Airport& a1);
    static Route from_airports_with_aircraft(const Airport& a0, const Airport& a1, const Aircraft& ac, uint16_t trips_per_day = 1, User::GameMode game_mode = User::GameMode::EASY);

    static inline duckdb::unique_ptr<duckdb::QueryResult> __get_route_result(uint16_t id0, uint16_t id1);
    
    static inline double calc_distance(double lat1, double lon1, double lat2, double lon2);
    static inline double calc_distance(const Airport& a0, const Airport& a1);
    static inline double estimate_load(uint8_t reputation, double autoprice_ratio, bool has_stopover);

    static const string repr(const Route& r);
};