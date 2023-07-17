#include <math.h>
#include <vector>
#include <cmath>
#include <iostream>

#include "include/route.hpp"
#include "include/db.hpp"

constexpr double PI = 3.14159265358979323846;

Route::Route() : direct_distance(0.0), valid(false) {};

// basic route meta
Route Route::create(const Airport& ap1, const Airport& ap2) {
    if (ap1.id == ap2.id) throw std::invalid_argument("Cannot create route with same origin and destination");

    Database::DBRoute db_route = Database::Client()->get_dbroute_by_ids(ap1.id, ap2.id);
    Route route;
    route.pax_demand = PaxDemand(
        db_route.yd,
        db_route.jd,
        db_route.fd
    );
    route.direct_distance = calc_distance(ap1, ap2);
    route.valid = true;
    
    return route;
}

AircraftRoute::AircraftRoute() : valid(false) {};

AircraftRoute AircraftRoute::create(const Airport& a0, const Airport& a1, const Aircraft& ac, uint16_t trips_per_day, const User& user) {
    AircraftRoute acr;
    acr.route = Route::create(a0, a1);

    acr.needs_stopover = acr.route.direct_distance > ac.range;
    acr.stopover = acr.needs_stopover ? Stopover::find_by_efficiency(a0, a1, ac, user.game_mode) : Stopover();
    if (acr.needs_stopover && !acr.stopover.exists) return acr;
    
    acr._ac_type = ac.type;
    double load = user.load / 100.0;
    #pragma warning(disable:4244)
    PaxDemand pd_pf = PaxDemand(
        acr.route.pax_demand.y / trips_per_day / load,
        acr.route.pax_demand.j / trips_per_day / load,
        acr.route.pax_demand.f / trips_per_day / load
    );
    #pragma warning(default:4244)

    switch (ac.type) {
        case Aircraft::Type::PAX:
            acr.config = Aircraft::Config(
                PaxConfig::calc_pax_conf(
                    pd_pf,
                    static_cast<uint16_t>(ac.capacity),
                    acr.route.direct_distance,
                    user.game_mode
                )
            );
            acr.ticket = Ticket(PaxTicket::from_optimal(
                acr.route.direct_distance,
                user.game_mode
            ));
            acr.max_income = (
                acr.config.pax_config.y * acr.ticket.pax_ticket.y +
                acr.config.pax_config.j * acr.ticket.pax_ticket.j +
                acr.config.pax_config.f * acr.ticket.pax_ticket.f
            );
            break;
        case Aircraft::Type::CARGO:
            acr.config = Aircraft::Config(
                CargoConfig::calc_cargo_conf(
                    CargoDemand(pd_pf),
                    ac.capacity,
                    user.l_training
                )
            );
            acr.ticket = Ticket(CargoTicket::from_optimal(
                acr.route.direct_distance,
                user.game_mode
            ));
            acr.max_income = (
                acr.config.cargo_config.l * 0.7 * acr.ticket.cargo_ticket.l +
                acr.config.cargo_config.h * acr.ticket.cargo_ticket.h
            ) * ac.capacity / 100.0;
            break;
        case Aircraft::Type::VIP:
            acr.config = Aircraft::Config(
                PaxConfig::calc_pax_conf(
                    pd_pf,
                    static_cast<uint16_t>(ac.capacity),
                    acr.route.direct_distance,
                    user.game_mode
                )
            );
            acr.ticket = Ticket(VIPTicket::from_optimal(
                acr.route.direct_distance
            ));
            acr.max_income = (
                acr.config.pax_config.y * acr.ticket.pax_ticket.y +
                acr.config.pax_config.j * acr.ticket.pax_ticket.j +
                acr.config.pax_config.f * acr.ticket.pax_ticket.f
            );
            break;
    }
    acr.income = acr.max_income * load;
    acr.fuel = AircraftRoute::calc_fuel(ac, acr.stopover.exists ? acr.stopover.full_distance : acr.route.direct_distance, user);
    acr.co2 = AircraftRoute::calc_co2(ac, acr.config, acr.stopover.exists ? acr.stopover.full_distance : acr.route.direct_distance, load, user);

    acr.valid = true;
    return acr;
}

AircraftRoute::Stopover::Stopover() : exists(false) {}
AircraftRoute::Stopover::Stopover(const Airport& airport, double full_distance) : airport(airport), full_distance(full_distance), exists(true) {}
AircraftRoute::Stopover AircraftRoute::Stopover::find_by_efficiency(const Airport& origin, const Airport& destination, const Aircraft& aircraft, User::GameMode game_mode) {
    const auto& db = Database::Client();
    Airport candidate = Airport();
    double candidate_distance = 99999;
    
    const uint16_t rwy_requirement = game_mode == User::GameMode::EASY ? 0 : aircraft.rwy;
    const idx_t o_idx = Database::get_airport_idx_by_id(origin.id);
    const idx_t d_idx = Database::get_airport_idx_by_id(destination.id);
    for (const Airport& ap : db->airports) {
        if (ap.rwy < rwy_requirement || ap.id == origin.id || ap.id == destination.id) continue;
        idx_t this_idx = Database::get_airport_idx_by_id(ap.id);
        double d_o = db->routes[Database::get_dbroute_idx(o_idx, this_idx)].distance;
        if (d_o > aircraft.range || d_o < 100) continue;
        double d_d = db->routes[Database::get_dbroute_idx(this_idx, d_idx)].distance;
        if (d_d > aircraft.range || d_d < 100) continue;
        if (d_o + d_d < candidate_distance) {
            candidate = ap;
            candidate_distance = d_o + d_d;
        }
    }
    if (!candidate.valid) return Stopover();
    return Stopover(candidate, candidate_distance);
}

const string AircraftRoute::Stopover::repr(const Stopover& stopover) {
    if (!stopover.exists) return "<Stopover NONEXISTENT>";
    return "<Stopover airport=" + Airport::repr(stopover.airport) + " full_distance=" + to_string(stopover.full_distance) + ">";
}


double inline Route::calc_distance(double lat1, double lon1, double lat2, double lon2) {
    double dLat = (lat2 - lat1) * PI / 180.0;
    double dLon = (lon2 - lon1) * PI / 180.0;
    return 12742 * asin(sqrt(pow(sin(dLat / 2), 2) + cos(lat1 * PI / 180.0) * cos(lat2 * PI / 180.0) * pow(sin(dLon / 2), 2)));
}

double inline Route::calc_distance(const Airport& ap1, const Airport& ap2) {
    return calc_distance(ap1.lat, ap1.lng, ap2.lat, ap2.lng);
}

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

double inline AircraftRoute::calc_fuel(const Aircraft& ac, double distance, const User& user, uint8_t ci) {
    return (
        (1 - user.fuel_training / 100.0) *
        ceil(distance * 100.0) / 100.0 *
        (ac.fuel_mod ? 0.9 : 1) *
        ac.fuel *
        (ci/500.0 + 0.6)
    );
}

double inline AircraftRoute::calc_co2(const Aircraft& ac, const Aircraft::Config& cfg, double distance, double load, const User& user, uint8_t ci) {
    return (
        (1 - user.co2_training / 100.0) * (
            ceil(distance * 100.0) / 100.0 *
            (ac.co2_mod ? 0.9 : 1) *
            ac.co2 * (
                ac.type == Aircraft::Type::CARGO ?
                (cfg.cargo_config.l / 100.0 * 0.7 / 1000.0 + cfg.cargo_config.h / 100.0 / 500.0) * load * ac.capacity :
                (cfg.pax_config.y + cfg.pax_config.j * 2 + cfg.pax_config.f * 3) * load
            ) + (
                ac.type == Aircraft::Type::CARGO ?
                ac.capacity :
                cfg.pax_config.y + cfg.pax_config.j + cfg.pax_config.f
            )
        ) * (ci/2000.0 + 0.9)
    );
}

const string Route::repr(const Route& r) {
    string s;
    if (r.valid) {
        s = "<Route direct_distance=" + to_string(r.direct_distance) + 
            " dem=" + to_string(r.pax_demand.y) + "|" + to_string(r.pax_demand.j) + "|" + to_string(r.pax_demand.f) + ">";
    } else {
        s = "<Route INVALID>";
    }
    return s;
}

const string AircraftRoute::repr(const AircraftRoute& ar) {
    string s;
    if (ar.valid) {
        s = "<AircraftRoute route=" + Route::repr(ar.route);
        switch (ar._ac_type) {
            case Aircraft::Type::VIP:
            case Aircraft::Type::PAX:
                s += " config.pax_config" + PaxConfig::repr(ar.config.pax_config);
                break;
            case Aircraft::Type::CARGO:
                s += " config.cargo_config" + CargoConfig::repr(ar.config.cargo_config);
                break;
        }
        switch (ar._ac_type) {
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
        s += " max_income=" + to_string(ar.max_income) + " income=" + to_string(ar.income);
        s += " fuel=" + to_string(ar.fuel) + " co2=" + to_string(ar.co2);
        s += " needs_stopover=" + to_string(ar.needs_stopover) + " stopover=" + AircraftRoute::Stopover::repr(ar.stopover);
        s += ">";
    } else {
        s = "<AircraftRoute INVALID>";
    }
    return s;
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict to_dict(const Route& r) {
    return py::dict(
        "pax_demand"_a = to_dict(r.pax_demand),
        "cargo_demand"_a = to_dict(CargoDemand(r.pax_demand)),
        "direct_distance"_a = r.direct_distance
    );
}

py::dict to_dict(const AircraftRoute::Stopover& s) {
    return s.exists ? py::dict(
        "airport"_a = to_dict(s.airport),
        "full_distance"_a = s.full_distance,
        "exists"_a = true
    ) : py::dict(
        "exists"_a = false
    );
}

py::dict to_dict(const AircraftRoute& ar) {
    py::dict config_d;
    py::dict ticket_d;
    switch (ar._ac_type) {
        case Aircraft::Type::PAX:
            config_d = to_dict(ar.config.pax_config);
            ticket_d = to_dict(ar.ticket.pax_ticket);
            break;
        case Aircraft::Type::VIP:
            config_d = to_dict(ar.config.pax_config);
            ticket_d = to_dict(ar.ticket.vip_ticket);
            break;
        case Aircraft::Type::CARGO:
            config_d = to_dict(ar.config.cargo_config);
            ticket_d = to_dict(ar.ticket.cargo_ticket);
            break;
    }

    return py::dict(
        "route"_a = to_dict(ar.route),
        "config"_a = config_d,
        "ticket"_a = ticket_d,
        "max_income"_a = ar.max_income,
        "income"_a = ar.income,
        "fuel"_a = ar.fuel,
        "co2"_a = ar.co2,
        "needs_stopover"_a = ar.needs_stopover,
        "stopover"_a = to_dict(ar.stopover),
        "valid"_a = ar.valid
    );
}

void pybind_init_route(py::module_& m) {
    py::module_ m_route = m.def_submodule("route");
    
    py::class_<AircraftRoute> acr_class(m_route, "AircraftRoute");
    
    py::class_<Route>(m_route, "Route")
        .def_readonly("pax_demand", &Route::pax_demand)
        .def_readonly("direct_distance", &Route::direct_distance)
        .def_readonly("valid", &Route::valid)
        .def_static("create", &Route::create, "ap0"_a, "ap1"_a)
        .def("__repr__", &Route::repr)
        .def("to_dict", py::overload_cast<const Route&>(&to_dict));
    
    py::class_<AircraftRoute::Stopover>(acr_class, "Stopover")
        .def_readonly("airport", &AircraftRoute::Stopover::airport)
        .def_readonly("full_distance", &AircraftRoute::Stopover::full_distance)
        .def_readonly("exists", &AircraftRoute::Stopover::exists)
        .def_static("find_by_efficiency", &AircraftRoute::Stopover::find_by_efficiency, "origin"_a, "destination"_a, "aircraft"_a, "game_mode"_a)
        .def("__repr__", &AircraftRoute::Stopover::repr)
        .def("to_dict", py::overload_cast<const AircraftRoute::Stopover&>(&to_dict));
    
    acr_class
        .def_readonly("route", &AircraftRoute::route)
        .def_readonly("config", &AircraftRoute::config)
        .def_readonly("ticket", &AircraftRoute::ticket)
        .def_readonly("max_income", &AircraftRoute::max_income)
        .def_readonly("income", &AircraftRoute::income)
        .def_readonly("fuel", &AircraftRoute::fuel)
        .def_readonly("co2", &AircraftRoute::co2)
        .def_readonly("needs_stopover", &AircraftRoute::needs_stopover)
        .def_readonly("stopover", &AircraftRoute::stopover)
        .def_readonly("valid", &AircraftRoute::valid)
        .def_static("create", &AircraftRoute::create, "ap0"_a, "ap1"_a, "ac"_a, "trips_per_day"_a = 1, py::arg_v("user", User(), "am4utils._core.game.User()"))
        .def_static("estimate_load", &AircraftRoute::estimate_load, "reputation"_a = 87, "autoprice_ratio"_a = 1.06, "has_stopover"_a = false)
        .def_static("calc_fuel", &AircraftRoute::calc_fuel, "ac"_a, "distance"_a, py::arg_v("user", User(), "am4utils._core.game.User()"), "ci"_a = 200)
        .def_static("calc_co2", &AircraftRoute::calc_co2, "ac"_a, "cfg"_a, "distance"_a, "load"_a, py::arg_v("user", User(), "am4utils._core.game.User()"), "ci"_a = 200)
        .def("__repr__", &Route::repr)
        .def("to_dict", py::overload_cast<const AircraftRoute&>(&to_dict));
}
#endif