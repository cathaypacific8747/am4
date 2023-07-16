#include <math.h>
#include <vector>
#include <cmath>
#include <iostream>

#include "include/route.hpp"
#include "include/db.hpp"

constexpr double PI = 3.14159265358979323846;

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

AircraftRoute Route::assign(const Aircraft& ac, uint16_t trips_per_day, const User& user) const {
    return AircraftRoute::from(*this, ac, trips_per_day, user);
}

AircraftRoute::AircraftRoute() : valid(false) {};

// depending on ac type, populate either pax or cargo demands
AircraftRoute AircraftRoute::from(const Route& r, const Aircraft& ac, uint16_t trips_per_day, const User& user) {
    AircraftRoute acr;
    acr.route = r;

    acr.needs_stopover = acr.route.direct_distance > ac.range;
    acr.stopover = acr.needs_stopover ? Stopover::find_by_efficiency(acr.route.origin, acr.route.destination, ac, user.game_mode) : Stopover();
    acr.load = user.load / 100;

    #pragma warning(disable:4244)
    PaxDemand pd_pf = PaxDemand(
        r.pax_demand.y / trips_per_day / acr.load,
        r.pax_demand.j / trips_per_day / acr.load,
        r.pax_demand.f / trips_per_day / acr.load
    );
    #pragma warning(default:4244)

    switch (ac.type) {
        case Aircraft::Type::PAX:
            acr.aircraft = PurchasedAircraft(
                ac,
                PaxConfig::calc_pax_conf(
                    pd_pf,
                    static_cast<uint16_t>(ac.capacity),
                    r.direct_distance,
                    user.game_mode
                )
            );
            acr.ticket = Ticket(PaxTicket::from_optimal(
                r.direct_distance,
                user.game_mode
            ));
            acr.max_income = (
                acr.aircraft.config.pax_config.y * acr.ticket.pax_ticket.y +
                acr.aircraft.config.pax_config.j * acr.ticket.pax_ticket.j +
                acr.aircraft.config.pax_config.f * acr.ticket.pax_ticket.f
            );
            break;
        case Aircraft::Type::CARGO:
            acr.aircraft = PurchasedAircraft(
                ac,
                CargoConfig::calc_cargo_conf(
                    CargoDemand(pd_pf),
                    ac.capacity,
                    user.l_training
                )
            );
            acr.ticket = Ticket(CargoTicket::from_optimal(
                r.direct_distance,
                user.game_mode
            ));
            acr.max_income = (
                acr.aircraft.config.cargo_config.l * 0.7 * acr.ticket.cargo_ticket.l +
                acr.aircraft.config.cargo_config.h * acr.ticket.cargo_ticket.h
            ) * ac.capacity / 100.0;
            break;
        case Aircraft::Type::VIP:
            acr.aircraft = PurchasedAircraft(
                ac,
                PaxConfig::calc_pax_conf(
                    pd_pf,
                    static_cast<uint16_t>(ac.capacity),
                    r.direct_distance,
                    user.game_mode
                )
            );
            acr.ticket = Ticket(VIPTicket::from_optimal(
                r.direct_distance
            ));
            acr.max_income = (
                acr.aircraft.config.pax_config.y * acr.ticket.pax_ticket.y +
                acr.aircraft.config.pax_config.j * acr.ticket.pax_ticket.j +
                acr.aircraft.config.pax_config.f * acr.ticket.pax_ticket.f
            );
            break;
    }

    acr.valid = true;
    return acr;
}

AircraftRoute::Stopover::Stopover() : exists(false) {}
AircraftRoute::Stopover::Stopover(const Airport& airport, double full_distance) : airport(airport), full_distance(full_distance), exists(true) {}
AircraftRoute::Stopover AircraftRoute::Stopover::find_by_efficiency(const Airport& origin, const Airport& destination, const Aircraft& aircraft, User::GameMode game_mode) {
    uint16_t rwy_requirement = game_mode == User::GameMode::EASY ? 0 : aircraft.rwy;
    
    const auto& airport_cache = Database::Client()->airport_cache;
    uint16_t candidate_id = 0;
    double candidate_distance = 99999;
    for (int i = 0; i < AIRPORT_COUNT; i++) {
        const auto& ap = airport_cache[i];
        if (ap.rwy < rwy_requirement || ap.id == origin.id || ap.id == destination.id) continue;
        double d_o = Route::calc_distance(ap.lat, ap.lng, origin.lat, origin.lng);
        if (d_o > aircraft.range || d_o < 100) continue;
        double d_d = Route::calc_distance(ap.lat, ap.lng, destination.lat, destination.lng);
        if (d_d > aircraft.range || d_d < 100) continue;
        if (d_o + d_d < candidate_distance) {
            candidate_id = ap.id;
            candidate_distance = d_o + d_d;
        }
    }
    if (candidate_id == 0) return Stopover();
    auto result = Database::Client()->get_airport_by_id->Execute(candidate_id);
    CHECK_SUCCESS(result);
    duckdb::unique_ptr<duckdb::DataChunk> chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Stopover();
    return Stopover(Airport(chunk, 0), candidate_distance);
}

const string AircraftRoute::Stopover::repr(const Stopover& stopover) {
    if (!stopover.exists) return "<Stopover NONEXISTENT>";
    return "<Stopover airport=" + Airport::repr(stopover.airport) + " full_distance=" + to_string(stopover.full_distance) + ">";
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

// TODO: expose to pybind!
double inline AircraftRoute::estimate_load(double reputation, double autoprice_ratio, bool has_stopover) {
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
        s = "<AircraftRoute aircraft=" + PurchasedAircraft::repr(ar.aircraft) + " route=" + Route::repr(ar.route) + " max_income=" + to_string(ar.max_income);
        switch (ar.aircraft.type) {
            case Aircraft::Type::VIP:
                s += " ticket.vip_ticket=" + VIPTicket::repr(ar.ticket.vip_ticket);
                break;
            case Aircraft::Type::PAX:
                s += " ticket.pax_ticket=" + PaxTicket::repr(ar.ticket.pax_ticket);
                break;
            case Aircraft::Type::CARGO:
                s += " ticket.cargo_ticket=" + CargoTicket::repr(ar.ticket.cargo_ticket);
                break;
        }
        s += " stopover=" + AircraftRoute::Stopover::repr(ar.stopover);
        s += " max_income=" + to_string(ar.max_income) + " load=" + to_string(ar.load);
        s += ">";
    } else {
        s = "<AircraftRoute INVALID>";
    }
    return s;
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict route_to_dict(const Route& r) {
    return py::dict(
        "origin"_a = ap_to_dict(r.origin),
        "destination"_a = ap_to_dict(r.destination),
        "pax_demand"_a = pax_demand_to_dict(r.pax_demand),
        "cargo_demand"_a = cargo_demand_to_dict(CargoDemand(r.pax_demand)),
        "direct_distance"_a = r.direct_distance
    );
}

py::dict stopover_to_dict(const AircraftRoute::Stopover& s) {
    return s.exists ? py::dict(
        "airport"_a = ap_to_dict(s.airport),
        "full_distance"_a = s.full_distance,
        "exists"_a = true
    ) : py::dict(
        "exists"_a = false
    );
}

py::dict ac_route_to_dict(const AircraftRoute& ar) {
    py::dict ticket_d;
    switch (ar.aircraft.type) {
        case Aircraft::Type::PAX:
            ticket_d = paxticket_to_dict(ar.ticket.pax_ticket);
            break;
        case Aircraft::Type::VIP:
            ticket_d = vipticket_to_dict(ar.ticket.vip_ticket);
            break;
        case Aircraft::Type::CARGO:
            ticket_d = cargoticket_to_dict(ar.ticket.cargo_ticket);
            break;
    }

    return py::dict(
        "route"_a = route_to_dict(ar.route),
        "aircraft"_a = pac_to_dict(ar.aircraft),
        "ticket"_a = ticket_d,
        "max_income"_a = ar.max_income,
        "load"_a = ar.load,
        "needs_stopover"_a = ar.needs_stopover,
        "stopover"_a = stopover_to_dict(ar.stopover)
    );
}

void pybind_init_route(py::module_& m) {
    py::module_ m_route = m.def_submodule("route");
    
    py::class_<AircraftRoute> acr_class(m_route, "AircraftRoute");
    
    py::class_<Route>(m_route, "Route")
        .def_readonly("origin", &Route::origin)
        .def_readonly("destination", &Route::destination)
        .def_readonly("pax_demand", &Route::pax_demand)
        .def_readonly("direct_distance", &Route::direct_distance)
        .def_readonly("valid", &Route::valid)
        .def_static("create", &Route::create, "ap1"_a, "ap2"_a)
        .def("assign", &Route::assign, "ac"_a, "trips_per_day"_a = 1, py::arg_v("user", User(), "am4utils._core.game.User()"))
        .def("__repr__", &Route::repr)
        .def("to_dict", &route_to_dict);
    
    py::class_<AircraftRoute::Stopover>(acr_class, "Stopover")
        .def_readonly("airport", &AircraftRoute::Stopover::airport)
        .def_readonly("full_distance", &AircraftRoute::Stopover::full_distance)
        .def_readonly("exists", &AircraftRoute::Stopover::exists)
        .def_static("find_by_efficiency", &AircraftRoute::Stopover::find_by_efficiency, "origin"_a, "destination"_a, "aircraft"_a, "game_mode"_a)
        .def("__repr__", &AircraftRoute::Stopover::repr)
        .def("to_dict", &stopover_to_dict);
    
    acr_class
        .def_readonly("route", &AircraftRoute::route)
        .def_readonly("aircraft", &AircraftRoute::aircraft)
        .def_readonly("ticket", &AircraftRoute::ticket)
        .def_readonly("max_income", &AircraftRoute::max_income)
        .def_readonly("load", &AircraftRoute::load)
        .def_readonly("needs_stopover", &AircraftRoute::needs_stopover)
        .def_readonly("stopover", &AircraftRoute::stopover)
        .def_readonly("valid", &AircraftRoute::valid)
        .def_static("create", &AircraftRoute::from, "route"_a, "ac"_a, "trips_per_day"_a = 1, py::arg_v("user", User(), "am4utils._core.game.User()"))
        .def_static("estimate_load", &AircraftRoute::estimate_load, "reputation"_a = 87, "autoprice_ratio"_a = 1.06, "has_stopover"_a = false)
        .def("__repr__", &Route::repr)
        .def("to_dict", &ac_route_to_dict);
}
#endif