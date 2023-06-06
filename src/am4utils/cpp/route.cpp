#include <math.h>
#include <vector>
#include <cmath>
#include <iostream>
#include "include/db.hpp"
#include "include/airport.hpp"
#include "include/route.hpp"
#include "include/enums.h"

PaxTicket PaxTicket::from_optimal(float distance, GameMode game_mode) {
    PaxTicket ticket;
    if (game_mode == GameMode::EASY) {
        ticket.y = (uint16_t)(1.10 * (0.4 * distance + 170)) - 2;
        ticket.j = (uint16_t)(1.08 * (0.8 * distance + 560)) - 2;
        ticket.f = (uint16_t)(1.06 * (1.2 * distance + 1200)) - 2;
    } else {
        ticket.y = (uint16_t)(1.10 * (0.3 * distance + 150)) - 2;
        ticket.j = (uint16_t)(1.08 * (0.6 * distance + 500)) - 2;
        ticket.f = (uint16_t)(1.06 * (0.9 * distance + 1000)) - 2;
    }
    return ticket;
};

CargoTicket CargoTicket::from_optimal(float distance, GameMode game_mode) {
    CargoTicket ticket;
    if (game_mode == GameMode::EASY) {
        ticket.l = floorf(1.10 * (0.0948283724581252 * distance + 85.2045432642377000)) / 100;
        ticket.h = floorf(1.08 * (0.0689663577640275 * distance + 28.2981124272893000)) / 100;
    } else {
        ticket.l = floorf(1.10 * (0.0776321822039374 * distance + 85.0567600367807000)) / 100;
        ticket.h = floorf(1.08 * (0.0517742799409248 * distance + 24.6369915396414000)) / 100;
    }
    return ticket;
};

VIPTicket VIPTicket::from_optimal(float distance) {
    VIPTicket ticket;
    ticket.y = (uint16_t)(1.22 * 1.7489 * (0.4 * distance + 170)) - 2;
    ticket.j = (uint16_t)(1.20 * 1.7489 * (0.8 * distance + 560)) - 2;
    ticket.f = (uint16_t)(1.17 * 1.7489 * (1.2 * distance + 1200)) - 2;
    return ticket;
}

string Route::repr() {
    return "<Route origin.id=" + std::to_string(origin.id) + " destination.id=" + std::to_string(destination.id) + " distance=" + std::to_string(distance) + " pax_demand.y=" + std::to_string(pax_demand.y) + " pax_demand.j=" + std::to_string(pax_demand.j) + " pax_demand.f=" + std::to_string(pax_demand.f) + ">";
}

double Route::calc_distance(double lat1, double lon1, double lat2, double lon2) {
    double dLat = (lat2 - lat1) * PI / 180.0;
    double dLon = (lon2 - lon1) * PI / 180.0;
    return 12742 * asin(sqrt(pow(sin(dLat / 2), 2) + cos(lat1 * PI / 180.0) * cos(lat2 * PI / 180.0) * pow(sin(dLon / 2), 2)));
}

double Route::calc_distance(Airport a1, Airport a2) {
    return calc_distance(a1.lat, a1.lng, a2.lat, a2.lng);
}

Route Route::from_airports(Airport a1, Airport a2) {
    uint16_t id0;
    uint16_t id1;

    if (a1.id < a2.id) {
        id0 = a1.id;
        id1 = a2.id;
    } else if (a1.id > a2.id) {
        id0 = a2.id;
        id1 = a1.id;
    } else {
        throw std::invalid_argument("Cannot create route from same airport");
    }

    Route route;

    auto result = Database::Client()->get_route_demands_by_id->Execute(id0, id1);
    CHECK_SUCCESS(result);

    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return route;

    route.origin = a1;
    route.destination = a2;
    route.distance = calc_distance(a1, a2);
    route.pax_demand.y = chunk->GetValue(0, 0).GetValue<uint16_t>();
    route.pax_demand.j = chunk->GetValue(1, 0).GetValue<uint16_t>();
    route.pax_demand.f = chunk->GetValue(2, 0).GetValue<uint16_t>();
    
    route.valid = true;
    
    return route;
}