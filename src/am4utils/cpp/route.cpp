#include <math.h>
#include <vector>
#include <cmath>
#include <iostream>

#include "include/route.hpp"
#include "include/db.hpp"

Route::Route() : direct_distance(0.0), valid(false) {};

// creates a basic route, assignout aircraft or ticket information
Route Route::create(const Airport& ap1, const Airport& ap2) {
    auto result = _get_route_result(ap1.id, ap2.id);

    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Route();

    Route route;
    route.origin = ap1;
    route.destination = ap2;
    route.pax_demand = PaxDemand(chunk, 0);
    route.direct_distance = calc_distance(ap1, ap2);
    route.valid = true;
    
    return route;
}

AircraftRoute Route::assign(const Aircraft& ac, uint16_t trips_per_day, const User& user) {
    return AircraftRoute::from(*this, ac, trips_per_day, user);
}

AircraftRoute::AircraftRoute() : has_stopover(false), valid(false) {};

// depending on ac type, populate either pax or cargo demands
AircraftRoute AircraftRoute::from(const Route& r, const Aircraft& ac, uint16_t trips_per_day, const User& user) {
    AircraftRoute acr;
    acr.route = r;

    switch (ac.type) {
        case Aircraft::Type::PAX:
            acr.aircraft = PurchasedAircraft(
                ac,
                PaxConfig::calc_pax_conf(
                    r.pax_demand,
                    static_cast<uint16_t>(ac.capacity),
                    r.direct_distance,
                    trips_per_day,
                    user.game_mode
                )
            );
            acr.ticket = Ticket(PaxTicket::from_optimal(
                r.direct_distance,
                user.game_mode
            ));
            // acr.load = user.override_load ? user.load / 100.0 : estimate_load(acr.aircraft.reputation, acr.aircraft.autoprice_ratio);
            acr.income = (
                acr.aircraft.config.pax_config.y * acr.ticket.pax_ticket.y +
                acr.aircraft.config.pax_config.j * acr.ticket.pax_ticket.j +
                acr.aircraft.config.pax_config.f * acr.ticket.pax_ticket.f
            );
            break;
        case Aircraft::Type::CARGO:
            acr.aircraft = PurchasedAircraft(
                ac,
                CargoConfig::calc_cargo_conf(
                    CargoDemand(r.pax_demand),
                    ac.capacity,
                    trips_per_day
                )
            );
            acr.ticket = Ticket(CargoTicket::from_optimal(
                r.direct_distance,
                user.game_mode
            ));
            acr.income = (
                acr.aircraft.config.cargo_config.l * 0.7 * acr.ticket.cargo_ticket.l +
                acr.aircraft.config.cargo_config.h * acr.ticket.cargo_ticket.h
            ) * ac.capacity / 100.0 / 1000;
            break;
        case Aircraft::Type::VIP:
            acr.aircraft = PurchasedAircraft(
                ac,
                PaxConfig::calc_pax_conf(
                    r.pax_demand,
                    static_cast<uint16_t>(ac.capacity),
                    r.direct_distance,
                    trips_per_day,
                    user.game_mode
                )
            );
            acr.ticket = Ticket(VIPTicket::from_optimal(
                r.direct_distance
            ));
            acr.income = (
                acr.aircraft.config.pax_config.y * acr.ticket.pax_ticket.y +
                acr.aircraft.config.pax_config.j * acr.ticket.pax_ticket.j +
                acr.aircraft.config.pax_config.f * acr.ticket.pax_ticket.f
            );
            break;
    }
    
    acr.valid = true;
    return acr;
}

duckdb::unique_ptr<duckdb::QueryResult> inline Route::_get_route_result(uint16_t id0, uint16_t id1) {
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

double inline AircraftRoute::estimate_load(uint8_t reputation, double autoprice_ratio, bool has_stopover) {
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
    string s;
    if (r.valid) {
        s = "<Route " + to_string(r.origin.id) + "." + to_string(r.destination.id) + " direct=" + to_string(r.direct_distance) + "km"
            " dem=" + to_string(r.pax_demand.y) + "|" + to_string(r.pax_demand.j) + "|" + to_string(r.pax_demand.f) + ">";
    } else {
        s = "<Route INVALID>";
    }
    return s;
}

const string AircraftRoute::repr(const AircraftRoute& ar) {
    string s;
    if (ar.valid) {
        s = "<AircraftRoute " + PurchasedAircraft::repr(ar.aircraft) + " " + Route::repr(ar.route) + " income=" + to_string(ar.income);
        switch (ar.aircraft.type) {
            case Aircraft::Type::VIP:
                s += " ticket=" + VIPTicket::repr(ar.ticket.vip_ticket);
                break;
            case Aircraft::Type::PAX:
                s += " ticket=" + PaxTicket::repr(ar.ticket.pax_ticket);
                break;
            case Aircraft::Type::CARGO:
                s += " ticket=" + CargoTicket::repr(ar.ticket.cargo_ticket);
                break;
        }
        s += ">";
    } else {
        s = "<AircraftRoute INVALID>";
    }
    return s;
}