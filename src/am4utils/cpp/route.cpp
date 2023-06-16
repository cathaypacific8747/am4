#include <math.h>
#include <vector>
#include <cmath>
#include <iostream>

#include "include/route.hpp"
#include "include/db.hpp"

Route::Route() : valid(false) {};

// no airports given, return both pax and cargo demands
Route Route::from_airports(const Airport& ap1, const Airport& ap2) {
    auto result = __get_route_result(ap1.id, ap2.id);

    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Route();

    Route route;
    route.origin = ap1;
    route.destination = ap2;
    route.direct_distance = calc_distance(ap1, ap2);
    route.pax_demand = PaxDemand(*chunk, 0);
    route.cargo_demand = CargoDemand(*chunk, 0);
    
    route.valid = true;
    
    return route;
}

// depending on ac type, populate either pax or cargo demands
Route Route::from_airports_with_aircraft(const Airport& ap1, const Airport& ap2, const Aircraft& ac, uint16_t trips_per_day, User::GameMode game_mode) {
    auto result = __get_route_result(ap1.id, ap2.id);

    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Route();

    Route route;
    route.origin = ap1;
    route.destination = ap2;
    route.direct_distance = calc_distance(ap1, ap2);
    switch (ac.type) {
        case Aircraft::Type::PAX:
            route.pax_demand = PaxDemand(*chunk, 0);
            route.aircraft = PurchasedAircraft(
                ac,
                PaxConfig::calc_pax_conf(
                    route.pax_demand,
                    ac.capacity,
                    route.direct_distance,
                    trips_per_day,
                    game_mode
                )
            );
            route.ticket = Ticket(PaxTicket::from_optimal(
                route.direct_distance,
                game_mode
            ));
            route.income = route.aircraft.config.pax_config.y * route.ticket.pax_ticket.y + route.aircraft.config.pax_config.j * route.ticket.pax_ticket.j + route.aircraft.config.pax_config.f * route.ticket.pax_ticket.f;
            break;
        case Aircraft::Type::CARGO:
            route.cargo_demand = CargoDemand(*chunk, 0);
            route.aircraft = PurchasedAircraft(
                ac,
                CargoConfig::calc_cargo_conf(
                    route.cargo_demand,
                    ac.capacity,
                    trips_per_day
                )
            );
            route.ticket = Ticket(CargoTicket::from_optimal(
                route.direct_distance,
                game_mode
            ));
            route.income = route.aircraft.config.cargo_config.l * route.ticket.cargo_ticket.l + route.aircraft.config.cargo_config.h * route.ticket.cargo_ticket.h;
            break;
        case Aircraft::Type::VIP:
            route.pax_demand = PaxDemand(*chunk, 0);
            route.aircraft = PurchasedAircraft(
                ac,
                PaxConfig::calc_pax_conf(
                    route.pax_demand,
                    ac.capacity,
                    route.direct_distance,
                    trips_per_day,
                    game_mode
                )
            );
            route.ticket = Ticket(VIPTicket::from_optimal(
                route.direct_distance
            ));
            route.income = route.aircraft.config.pax_config.y * route.ticket.pax_ticket.y + route.aircraft.config.pax_config.j * route.ticket.pax_ticket.j + route.aircraft.config.pax_config.f * route.ticket.pax_ticket.f;
            break;
    }
    
    route.valid = true;
    
    return route;
}

duckdb::unique_ptr<duckdb::QueryResult> inline Route::__get_route_result(uint16_t id0, uint16_t id1) {
    if (id0 < id1) {
        auto result = Database::Client()->get_route_demands_by_id->Execute(id0, id1);
        CHECK_SUCCESS(result);
        return result;
    } else if (id0 > id1) {
        auto result = Database::Client()->get_route_demands_by_id->Execute(id1, id0);
        CHECK_SUCCESS(result);
        return result;
    }
    throw std::invalid_argument("Cannot create route from same airport");
}


double inline Route::calc_distance(double lat1, double lon1, double lat2, double lon2) {
    double dLat = (lat2 - lat1) * PI / 180.0;
    double dLon = (lon2 - lon1) * PI / 180.0;
    return 12742 * asin(sqrt(pow(sin(dLat / 2), 2) + cos(lat1 * PI / 180.0) * cos(lat2 * PI / 180.0) * pow(sin(dLon / 2), 2)));
}

double inline Route::calc_distance(const Airport& ap1, const Airport& ap2) {
    return calc_distance(ap1.lat, ap1.lng, ap2.lat, ap2.lng);
}

double inline estimate_load(uint8_t reputation, double autoprice_ratio, bool has_stopover) {
    if (autoprice_ratio > 1) { // normal (sorta triangular?) distribution, [Z+(0: .00019, 1: .0068, 2: .0092), max: .001] * reputation
        if (has_stopover) {
            return 0.0085855 * reputation;
        } else {
            return 0.0090435 * reputation;
        }
    } else { // uniform distribution: +- 0.00052 * reputation
        double base_load;
        if (has_stopover) {
            base_load = 0.0090312 * reputation;
        } else {
            base_load = 0.0095265 * reputation;
        }
        return (base_load - 1) * autoprice_ratio + 1;
    }
}

const string Route::repr(const Route& r) {
    if (!r.valid) return "<Route invalid>";
    std::string s = "<Route " + to_string(r.origin.id) + "->" + to_string(r.destination.id) + " direct=" + to_string(r.direct_distance) + "km"
                    " pax_dem=" + to_string(r.pax_demand.y) + "|" + to_string(r.pax_demand.j) + "|" + to_string(r.pax_demand.f) +
                    " cargo_dem=" + to_string(r.cargo_demand.l) + "|" + to_string(r.cargo_demand.h) + ">";
    return s;
}