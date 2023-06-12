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

PaxDemand::PaxDemand() : y(0), j(0), f(0) {};
PaxDemand::PaxDemand(uint16_t y, uint16_t j, uint16_t f) : y(y), j(j), f(f) {};
PaxDemand::PaxDemand(const duckdb::DataChunk& chunk, idx_t row) :
    y(chunk.GetValue(0, row).GetValue<uint16_t>()),
    j(chunk.GetValue(1, row).GetValue<uint16_t>()),
    f(chunk.GetValue(2, row).GetValue<uint16_t>()) {};

CargoDemand::CargoDemand() : l(0), h(0) {};
CargoDemand::CargoDemand(uint32_t l, uint32_t h) : l(l), h(h) {};
CargoDemand::CargoDemand(uint16_t y, uint16_t j) : l(y * 1000), h(round((float)j / 2) * 1000) {};
CargoDemand::CargoDemand(const duckdb::DataChunk& chunk, idx_t row) :
    l(chunk.GetValue(0, row).GetValue<int32_t>() * 1000),
    h(round(chunk.GetValue(1, row).GetValue<float>() / 2) * 1000) {};
CargoDemand::CargoDemand(const PaxDemand& pax_demand) : l(pax_demand.y * 1000), h(round(pax_demand.j / 2) * 500) {};

Route::Route() : valid(false) {};

double inline Route::calc_distance(double lat1, double lon1, double lat2, double lon2) {
    double dLat = (lat2 - lat1) * PI / 180.0;
    double dLon = (lon2 - lon1) * PI / 180.0;
    return 12742 * asin(sqrt(pow(sin(dLat / 2), 2) + cos(lat1 * PI / 180.0) * cos(lat2 * PI / 180.0) * pow(sin(dLon / 2), 2)));
}

double inline Route::calc_distance(const Airport& ap1, const Airport& ap2) {
    return calc_distance(ap1.lat, ap1.lng, ap2.lat, ap2.lng);
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

// no airports given, return both pax and cargo demands
Route Route::from_airports(const Airport& ap1, const Airport& ap2) {
    auto result = __get_route_result(ap1.id, ap2.id);

    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Route();

    Route route;
    route.origin = ap1;
    route.destination = ap2;
    route.distance = calc_distance(ap1, ap2);
    route.pax_demand = PaxDemand(*chunk, 0);
    route.cargo_demand = CargoDemand(*chunk, 0);
    
    route.valid = true;
    
    return route;
}

// depending on ac type, populate either pax or cargo demands
Route Route::from_airports_with_aircraft(const Airport& ap1, const Airport& ap2, const Aircraft& ac) {
    auto result = __get_route_result(ap1.id, ap2.id);

    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Route();

    Route route;
    route.origin = ap1;
    route.destination = ap2;
    route.distance = calc_distance(ap1, ap2);
    switch (ac.type) {
        case AircraftType::PAX:
        case AircraftType::VIP:
            route.pax_demand = PaxDemand(*chunk, 0);
            break;
        case AircraftType::CARGO:
            route.cargo_demand = CargoDemand(*chunk, 0);
            break;
    }
    
    route.valid = true;
    
    return route;
}

const string Route::repr() {
    if (!valid) return "<Route valid=false>";
    std::string s = "<Route origin.id=" + std::to_string(origin.id) + " destination.id=" + std::to_string(destination.id) + " distance=" + std::to_string(distance) +
                    " pax_demand=(" + std::to_string(pax_demand.y) + ", " + std::to_string(pax_demand.j) + ", " + std::to_string(pax_demand.f) + ")" +
                    " cargo_demand=(" + std::to_string(cargo_demand.l) + ", " + std::to_string(cargo_demand.h) + ")>";
    return s;
}