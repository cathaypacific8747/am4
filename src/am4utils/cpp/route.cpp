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
CargoDemand::CargoDemand(uint16_t y, uint16_t j) : l(y * 1000), h(round((j / 2.0F) * 1000)) {};
CargoDemand::CargoDemand(const duckdb::DataChunk& chunk, idx_t row) :
    l(chunk.GetValue(0, row).GetValue<int32_t>() * 1000),
    h(round(chunk.GetValue(1, row).GetValue<float>() / 2) * 1000) {};
CargoDemand::CargoDemand(const PaxDemand& pax_demand) : l(pax_demand.y * 1000), h(round(pax_demand.j / 2.0F) * 500) {};

Route::Route() : valid(false) {};

double inline Route::calc_distance(double lat1, double lon1, double lat2, double lon2) {
    double dLat = (lat2 - lat1) * PI / 180.0;
    double dLon = (lon2 - lon1) * PI / 180.0;
    return 12742 * asin(sqrt(pow(sin(dLat / 2), 2) + cos(lat1 * PI / 180.0) * cos(lat2 * PI / 180.0) * pow(sin(dLon / 2), 2)));
}

double inline Route::calc_distance(const Airport& ap1, const Airport& ap2) {
    return calc_distance(ap1.lat, ap1.lng, ap2.lat, ap2.lng);
}


PaxConfig Route::calc_fjy_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.f = d_pf.f * 3 > capacity ? capacity / 3 : d_pf.f;
    config.j = d_pf.f * 3 + d_pf.j * 2 > capacity ? (capacity - config.f * 3) / 2 : d_pf.j;
    config.y = capacity - config.f * 3 - config.j * 2;
    config.valid = config.y < d_pf.y;
    config.algorithm = PaxConfigAlgorithm::FJY;
    return config;
};

PaxConfig Route::calc_fyj_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.f = d_pf.f * 3 > capacity ? capacity / 3 : d_pf.f;
    config.y = d_pf.f * 3 + d_pf.y > capacity ? capacity - config.f * 3 : d_pf.y;
    config.j = (capacity - config.f * 3 - config.y) / 2;
    config.valid = config.j < d_pf.j;
    config.algorithm = PaxConfigAlgorithm::FYJ;
    return config;
};

PaxConfig Route::calc_jfy_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.j = d_pf.j * 2 > capacity ? capacity / 2 : d_pf.j;
    config.f = d_pf.j * 2 + d_pf.f * 3 > capacity ? (capacity - config.j * 2) / 3 : d_pf.f;
    config.y = capacity - config.j * 2 - config.f * 3;
    config.valid = config.y < d_pf.y;
    config.algorithm = PaxConfigAlgorithm::JFY;
    return config;
};

PaxConfig Route::calc_jyf_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.j = d_pf.j * 2 > capacity ? capacity / 2 : d_pf.j;
    config.y = d_pf.j * 2 + d_pf.y > capacity ? capacity - config.j * 2 : d_pf.y;
    config.f = capacity - config.y - config.j * 2;
    config.valid = config.f < d_pf.f;
    config.algorithm = PaxConfigAlgorithm::JYF;
    return config;
};

PaxConfig Route::calc_yfj_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.y = d_pf.y > capacity ? capacity : d_pf.y;
    config.f = d_pf.y + d_pf.f * 3 > capacity ? (capacity - config.y) / 3 : d_pf.f;
    config.j = (capacity - config.y - config.f * 3) / 2;
    config.valid = config.j < d_pf.j;
    config.algorithm = PaxConfigAlgorithm::YFJ;
    return config;
};

PaxConfig Route::calc_yjf_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.y = d_pf.y > capacity ? capacity : d_pf.y;
    config.j = d_pf.y + d_pf.j * 2 > capacity ? (capacity - config.y) / 2 : d_pf.j;
    config.f = capacity - config.y - config.j * 2;
    config.valid = config.f < d_pf.f;
    config.algorithm = PaxConfigAlgorithm::YJF;
    return config;
};

PaxConfig Route::calc_pax_conf(const PaxDemand& pax_demand, uint16_t capacity, float distance, uint16_t trips_per_day, GameMode game_mode) {
    PaxDemand d_pf = PaxDemand(
        pax_demand.y / trips_per_day,
        pax_demand.j / trips_per_day,
        pax_demand.f / trips_per_day
    );

    PaxConfig config;
    if (game_mode == GameMode::EASY) {
        if (distance < 14425) {
            config = calc_fjy_conf(d_pf, capacity, distance);
        } else if (distance < 14812) {
            config = calc_fyj_conf(d_pf, capacity, distance);
        } else if (distance < 15200) {
            config = calc_yfj_conf(d_pf, capacity, distance);
        } else {
            config = calc_yjf_conf(d_pf, capacity, distance);
        }
    } else {
        if (distance < 13888.88) {
            config = calc_fjy_conf(d_pf, capacity, distance);
        } else if (distance < 15694.44) {
            config = calc_jfy_conf(d_pf, capacity, distance);
        } else if (distance < 17500) {
            config = calc_jyf_conf(d_pf, capacity, distance);
        } else {
            config = calc_yjf_conf(d_pf, capacity, distance);
        }
    }
    return config;
}

CargoConfig Route::calc_cargo_conf(const CargoDemand& cargo_demand, uint32_t capacity, uint16_t trips_per_day, uint8_t l_training) {
    // always fill up low priority first
    CargoDemand d_pf = CargoDemand(
        cargo_demand.l / trips_per_day,
        cargo_demand.h / trips_per_day
    );

    double l_cap = capacity * (1 + l_training / 100.0) * 0.7;

    CargoConfig config;
    if (d_pf.l > l_cap) {
        config.l = 100;
        config.h = 0;
        config.valid = true;
    } else {
        config.l = d_pf.l / l_cap * 100;
        config.h = 100 - config.l;
        config.valid = d_pf.h >= (l_cap - d_pf.l) / 0.7;
    }
    return config;
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
Route Route::from_airports_with_aircraft(const Airport& ap1, const Airport& ap2, const Aircraft& ac, uint16_t trips_per_day, GameMode game_mode) {
    auto result = __get_route_result(ap1.id, ap2.id);

    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Route();

    Route route;
    route.origin = ap1;
    route.destination = ap2;
    route.distance = calc_distance(ap1, ap2);
    switch (ac.type) {
        case AircraftType::PAX:
            route.pax_demand = PaxDemand(*chunk, 0);
            route.purchased_aircraft = PurchasedAircraft(
                ac,
                PurchasedAircaftConfig(Route::calc_pax_conf(
                    route.pax_demand,
                    ac.capacity,
                    route.distance,
                    trips_per_day,
                    game_mode
                ))
            );
            route.ticket = Ticket(PaxTicket::from_optimal(
                route.distance,
                game_mode
            ));
            break;
        case AircraftType::CARGO:
            route.cargo_demand = CargoDemand(*chunk, 0);
            route.purchased_aircraft = PurchasedAircraft(
                ac,
                PurchasedAircaftConfig(Route::calc_cargo_conf(
                    route.cargo_demand,
                    ac.capacity,
                    trips_per_day
                ))
            );
            route.ticket = Ticket(CargoTicket::from_optimal(
                route.distance,
                game_mode
            ));
            break;
        case AircraftType::VIP:
            route.pax_demand = PaxDemand(*chunk, 0);
            route.purchased_aircraft = PurchasedAircraft(
                ac,
                PurchasedAircaftConfig(Route::calc_pax_conf(
                    route.pax_demand,
                    ac.capacity,
                    route.distance,
                    trips_per_day,
                    game_mode
                ))
            );
            route.ticket = Ticket(VIPTicket::from_optimal(
                route.distance
            ));
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