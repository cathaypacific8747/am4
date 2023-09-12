#include <math.h>
#include <vector>
#include <cmath>
#include <iostream>

#include "include/route.hpp"
#include "include/db.hpp"

using std::get;

Route::Route() : direct_distance(0.0), valid(false) {};

// basic route meta
Route Route::create(const Airport& ap1, const Airport& ap2) {
    if (ap1.id == ap2.id) throw std::invalid_argument("Cannot create route with same origin and destination");

    const auto& db = Database::Client();
    const uint16_t o_idx = db->airport_id_hashtable[ap1.id];
    const uint16_t d_idx = db->airport_id_hashtable[ap2.id];
    
    Route route;
    route.pax_demand = db->pax_demands[db->get_dbroute_idx(o_idx, d_idx)];
    route.direct_distance = db->distances[o_idx][d_idx];
    route.valid = true;
    return route;
}

inline double Route::calc_distance(double lat1, double lon1, double lat2, double lon2) {
    double dLat = (lat2 - lat1) * M_PI / 180.0;
    double dLon = (lon2 - lon1) * M_PI / 180.0;
    return 12742 * asin(sqrt(pow(sin(dLat / 2), 2) + cos(lat1 * M_PI / 180.0) * cos(lat2 * M_PI / 180.0) * pow(sin(dLon / 2), 2)));
}

inline double Route::calc_distance(const Airport& ap1, const Airport& ap2) {
    return calc_distance(ap1.lat, ap1.lng, ap2.lat, ap2.lng);
}

// TODO: use one template function for both pax and cargo
template <bool is_vip>
inline void AircraftRoute::update_pax_details(uint16_t ac_capacity, const AircraftRoute::Options& options, const User& user) {
    const Aircraft::PaxConfig::Algorithm config_algorithm = std::holds_alternative<std::monostate>(options.config_algorithm) ? Aircraft::PaxConfig::Algorithm::AUTO : get<Aircraft::PaxConfig::Algorithm>(options.config_algorithm);    
    const PaxDemand load_adj_pd = this->route.pax_demand / user.load;
    uint16_t tpd = 1;
    if (options.tpd_mode == AircraftRoute::Options::TPDMode::AUTO_MULTIPLE_OF || options.tpd_mode == AircraftRoute::Options::TPDMode::STRICT)
        tpd = options.trips_per_day;

    auto calc_cfg = [&](uint16_t tpd) {
        return Aircraft::PaxConfig::calc_pax_conf(
            load_adj_pd / tpd,
            ac_capacity,
            this->route.direct_distance,
            user.game_mode,
            config_algorithm
        );
    };
    auto calc_max_rawincome = [&](const Aircraft::PaxConfig& cfg, const PaxTicket& tkt) -> uint32_t {
        return (
            cfg.y * tkt.y +
            cfg.j * tkt.j +
            cfg.f * tkt.f
        );
    };
    Aircraft::PaxConfig cfg = calc_cfg(tpd);
    if (!cfg.valid) {
        this->warnings.push_back(AircraftRoute::Warning::ERR_INSUFFICIENT_DEMAND);
        this->valid = false;
        return;
    }
    const PaxTicket tkt = [&]() {
        if constexpr(is_vip)
            return static_cast<PaxTicket>(
                VIPTicket::from_optimal(this->route.direct_distance)
            );
        else
            return PaxTicket::from_optimal(
                this->route.direct_distance,
                user.game_mode
            );
    }();
    uint32_t max_rawincome = calc_max_rawincome(cfg, tkt);
    if (options.tpd_mode == AircraftRoute::Options::TPDMode::STRICT) {
        this->ticket = tkt;
        this->config = cfg;
        this->max_income = 0; // we don't know whether higher tpds will yield higher income - this part is handled by AircraftRoute::update_max_income()
        this->income = max_rawincome * user.load;
        this->trips_per_day = options.trips_per_day;
    } else {
        // start searching for alternative candidates
        // note: the configuration formula always fills up a specific class before moving on, and if the tpd is:
        //   - low, we can almost guarantee that the optimum class is filled up first but we will end up wasting seats;
        //   - high, the max_income is less optimal because seats are distributed, but this will allow a greater *total* income.
        //     for top-level gameplay, we often value route availability over profitability.
        // so, here we will return the highest tpd that is within X% of the max_income. (X is user-defined.)
        uint16_t c_tpd = tpd;
        double c_max_rawincome = max_rawincome;
        Aircraft::PaxConfig c_cfg = cfg;
        
        double max_rawincome_bound = max_rawincome * (1 - user.income_loss_tol);
        uint16_t incr = 1;
        if (options.tpd_mode == AircraftRoute::Options::TPDMode::AUTO_MULTIPLE_OF)
            incr = options.trips_per_day;
        for (tpd += incr; tpd < 1500 * incr; tpd += incr) {
            cfg = calc_cfg(tpd);
            if (!cfg.valid) // demand exhausted
                break;
            const uint32_t this_max_rawincome = calc_max_rawincome(cfg, tkt);
            if (this_max_rawincome < max_rawincome_bound)
                break;
            c_tpd = tpd;
            c_max_rawincome = this_max_rawincome;
            c_cfg = cfg;
            if (this_max_rawincome > max_rawincome) // unlikely since first tpd is likely already max
                max_rawincome = this_max_rawincome;
        }
        this->max_income = max_rawincome * user.load;
        this->ticket = tkt;
        this->config = c_cfg;
        this->income = c_max_rawincome * user.load;
        this->trips_per_day = c_tpd;
    }
    this->valid = true;
}

inline void AircraftRoute::update_cargo_details(uint32_t ac_capacity, const AircraftRoute::Options& options, const User& user) {
    const Aircraft::CargoConfig::Algorithm config_algorithm = std::holds_alternative<std::monostate>(options.config_algorithm) ? Aircraft::CargoConfig::Algorithm::AUTO : get<Aircraft::CargoConfig::Algorithm>(options.config_algorithm);
    const CargoDemand load_adj_cd = CargoDemand(this->route.pax_demand);
    uint16_t tpd = 1;
    if (options.tpd_mode == AircraftRoute::Options::TPDMode::AUTO_MULTIPLE_OF || options.tpd_mode == AircraftRoute::Options::TPDMode::STRICT)
        tpd = options.trips_per_day;
    
    auto calc_conf = [&](uint16_t trips_per_day) {
        return Aircraft::CargoConfig::calc_cargo_conf(
            load_adj_cd / user.load / trips_per_day,
            ac_capacity,
            user.l_training,
            user.h_training,
            config_algorithm
        );
    };
    auto calc_rawincome = [&](const Aircraft::CargoConfig& cfg, const CargoTicket& tkt) -> double {
        return (
            (1 + user.l_training / 100.0) * cfg.l * 0.7 * tkt.l +
            (1 + user.h_training / 100.0) * cfg.h * tkt.h
        ) * ac_capacity / 100.0;
    };

    Aircraft::CargoConfig cfg = calc_conf(tpd);
    if (!cfg.valid) {
        this->warnings.push_back(AircraftRoute::Warning::ERR_INSUFFICIENT_DEMAND);
        this->valid = false;
        return;
    }
    const CargoTicket tkt = CargoTicket::from_optimal(
        this->route.direct_distance,
        user.game_mode
    );
    double max_rawincome = calc_rawincome(cfg, tkt);
    if (options.tpd_mode == AircraftRoute::Options::TPDMode::STRICT) {
        this->ticket = tkt;
        this->config = cfg;
        this->max_income = 0;
        this->income = max_rawincome * user.load;
        this->trips_per_day = options.trips_per_day;
    } else {
        uint16_t c_tpd = tpd;
        double c_max_rawincome = max_rawincome;
        Aircraft::Config c_cfg = cfg;
        
        double max_rawincome_bound = max_rawincome * (1 - user.income_loss_tol);
        uint16_t incr = 1;
        if (options.tpd_mode == AircraftRoute::Options::TPDMode::AUTO_MULTIPLE_OF)
            incr = options.trips_per_day;
        for (tpd += incr; tpd < 1500 * incr; tpd += incr) {
            cfg = calc_conf(tpd);
            if (!cfg.valid)
                break;
            const double this_max_rawincome = calc_rawincome(cfg, tkt);
            if (this_max_rawincome < max_rawincome_bound)
                break;
            c_tpd = tpd;
            c_max_rawincome = this_max_rawincome;
            c_cfg = cfg;
            if (this_max_rawincome > max_rawincome)
                max_rawincome = this_max_rawincome;
        }
        this->max_income = max_rawincome * user.load;
        this->ticket = tkt;
        this->config = c_cfg;
        this->income = c_max_rawincome * user.load;
        this->trips_per_day = c_tpd;
    }
    this->valid = true;
}

AircraftRoute::AircraftRoute() : valid(false) {};
AircraftRoute::Options::Options(TPDMode tpd_mode, uint16_t trips_per_day, double max_distance, float max_flight_time, ConfigAlgorithm config_algorithm) : tpd_mode(tpd_mode), trips_per_day(trips_per_day), max_distance(max_distance), max_flight_time(max_flight_time), config_algorithm(config_algorithm) {
    if (tpd_mode == AircraftRoute::Options::TPDMode::AUTO && trips_per_day != 1)
        std::cerr << "WARN: trips_per_day is ignored when tpd_mode is AUTO" << std::endl;
};
AircraftRoute AircraftRoute::create(const Airport& a0, const Airport& a1, const Aircraft& ac, const AircraftRoute::Options& options, const User& user) {
    AircraftRoute acr;
    acr.route = Route::create(a0, a1);
    acr._ac_type = ac.type;

    if (user.game_mode == User::GameMode::REALISM && a1.rwy < ac.rwy) {
        acr.warnings.push_back(AircraftRoute::Warning::ERR_RWY_TOO_SHORT);
        return acr;
    }
    if (acr.route.direct_distance > options.max_distance) {
        acr.warnings.push_back(AircraftRoute::Warning::ERR_DISTANCE_ABOVE_SPECIFIED);
        return acr;
    } else if (acr.route.direct_distance > 2 * ac.range) {
        acr.warnings.push_back(AircraftRoute::Warning::ERR_DISTANCE_TOO_LONG);
        return acr;
    } else if (acr.route.direct_distance < 100) {
        acr.warnings.push_back(AircraftRoute::Warning::ERR_DISTANCE_TOO_SHORT);
        return acr;
    } else if (acr.route.direct_distance < 1000) {
        acr.warnings.push_back(AircraftRoute::Warning::REDUCED_CONTRIBUTION);
    }
    acr.needs_stopover = acr.route.direct_distance > ac.range;
    acr.stopover = acr.needs_stopover ? Stopover::find_by_efficiency(a0, a1, ac, user.game_mode) : Stopover();
    if (acr.needs_stopover && !acr.stopover.exists) {
        acr.warnings.push_back(AircraftRoute::Warning::ERR_NO_STOPOVER);
        return acr;
    }
    const double full_distance = acr.stopover.exists ? acr.stopover.full_distance : acr.route.direct_distance;
    acr.flight_time = static_cast<float>(full_distance) / (ac.speed * (user.game_mode == User::GameMode::EASY ? 1.5f : 1.0f));
    if (acr.flight_time > options.max_flight_time) {
        acr.warnings.push_back(AircraftRoute::Warning::ERR_FLIGHT_TIME_ABOVE_SPECIFIED);
        return acr;
    }
    
    switch (ac.type) {
        case Aircraft::Type::PAX:
        {
            acr.update_pax_details<false>(
                static_cast<uint16_t>(ac.capacity),
                options,
                user
            );
            if (!acr.valid) return acr;
            acr.co2 = AircraftRoute::calc_co2(ac, get<Aircraft::PaxConfig>(acr.config), full_distance, user);
            break;
        }
        case Aircraft::Type::CARGO:
        {
            acr.update_cargo_details(
                static_cast<uint32_t>(ac.capacity),
                options,
                user
            );
            if (!acr.valid) return acr;
            acr.co2 = AircraftRoute::calc_co2(ac, get<Aircraft::CargoConfig>(acr.config), full_distance, user);
            break;
        }
        case Aircraft::Type::VIP:
        {
            acr.update_pax_details<true>(
                static_cast<uint16_t>(ac.capacity),
                options,
                user
            );
            if (!acr.valid) return acr;
            acr.co2 = AircraftRoute::calc_co2(ac, get<Aircraft::PaxConfig>(acr.config), full_distance, user);
            break;
        }
    }
    acr.fuel = AircraftRoute::calc_fuel(ac, full_distance, user);
    acr.acheck_cost = static_cast<float>(ac.check_cost) * acr.flight_time / static_cast<float>(ac.maint);
    acr.repair_cost = ac.cost / 1000.0 * 0.0075 * (1 - 2 * user.repair_training / 100.0); // each flight adds random [0, 1.5]% wear, each tp decreases wear by 2% 
    acr.profit = (
        acr.income
        - acr.fuel * user.fuel_price / 1000.0
        - acr.co2 * user.co2_price / 1000.0
        - acr.acheck_cost
        - acr.repair_cost
    );
    acr.ci = 200;
    acr.contribution = AircraftRoute::calc_contribution(full_distance, user, 200);

    acr.valid = true;
    return acr;
}

AircraftRoute::Stopover::Stopover() : exists(false) {}
AircraftRoute::Stopover::Stopover(const Airport& airport, double full_distance) : airport(airport), full_distance(full_distance), exists(true) {}
AircraftRoute::Stopover AircraftRoute::Stopover::find_by_efficiency(const Airport& origin, const Airport& destination, const Aircraft& aircraft, User::GameMode game_mode) {
    const auto& db = Database::Client();
    const auto& airports = db->airports;
    const auto& distances = db->distances;
    Airport candidate = Airport();
    double candidate_distance = 99999;
    
    const double ac_range = static_cast<double>(aircraft.range);
    const uint16_t o_idx = db->airport_id_hashtable[origin.id];
    const uint16_t d_idx = db->airport_id_hashtable[destination.id];
    // d_o & d_d will catch cases where idx == o_idx || idx == d_idx
    if (game_mode == User::GameMode::EASY) {
        for (uint16_t idx = 0; idx < AIRPORT_COUNT; idx++) {
            const Airport& ap = airports[idx];
            const double d_o = distances[o_idx][idx];
            if (d_o > ac_range || d_o < 100.0) continue;
            const double d_d = distances[d_idx][idx];
            if (d_d > ac_range || d_d < 100.0) continue;
            if (d_o + d_d < candidate_distance) {
                candidate = ap;
                candidate_distance = d_o + d_d;
            }
        }
    } else {
        const uint16_t rwy_requirement = aircraft.rwy;
        for (uint16_t idx = 0; idx < AIRPORT_COUNT; idx++) {
            const Airport& ap = airports[idx];
            if (ap.rwy < rwy_requirement) continue;
            const double d_o = distances[o_idx][idx];
            if (d_o > ac_range || d_o < 100.0) continue;
            const double d_d = distances[d_idx][idx];
            if (d_d > ac_range || d_d < 100.0) continue;
            if (d_o + d_d < candidate_distance) {
                candidate = ap;
                candidate_distance = d_o + d_d;
            }
        }
    }

    if (!candidate.valid) return Stopover();
    return Stopover(candidate, candidate_distance);
}

const string AircraftRoute::Stopover::repr(const Stopover& stopover) {
    if (!stopover.exists) return "<Stopover NONEXISTENT>";
    return "<Stopover airport=" + Airport::repr(stopover.airport) + " full_distance=" + to_string(stopover.full_distance) + ">";
}

inline double AircraftRoute::estimate_load(double reputation, double autoprice_ratio, bool has_stopover) {
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

inline double AircraftRoute::calc_fuel(const Aircraft& ac, double distance, const User& user, uint8_t ci) {
    return (
        (1 - user.fuel_training / 100.0) *
        ceil(distance * 100.0) / 100.0 *
        (ac.fuel_mod ? 0.9 : 1) *
        ac.fuel *
        (ci/500.0 + 0.6)
    );
}

inline double AircraftRoute::calc_co2(const Aircraft& ac, const Aircraft::PaxConfig& cfg, double distance, const User& user, uint8_t ci) {
    return (
        (1 - user.co2_training / 100.0) * (
            ceil(distance * 100.0) / 100.0 *
            (ac.co2_mod ? 0.9 : 1) *
            ac.co2 * (
                (cfg.y + cfg.j * 2 + cfg.f * 3) * user.load
            ) + (
                cfg.y + cfg.j + cfg.f
            )
        ) * (ci/2000.0 + 0.9)
    );
}

inline double AircraftRoute::calc_co2(const Aircraft& ac, const Aircraft::CargoConfig& cfg, double distance, const User& user, uint8_t ci) {
    return (
        (1 - user.co2_training / 100.0) * (
            ceil(distance * 100.0) / 100.0 *
            (ac.co2_mod ? 0.9 : 1) *
            ac.co2 * (
                (cfg.l / 100.0 * 0.7 / 1000.0 + cfg.h / 100.0 / 500.0) * user.load * ac.capacity
            ) + (
                (cfg.l / 100.0 * 0.7 + cfg.h / 100.0) * ac.capacity
            )
        ) * (ci/2000.0 + 0.9)
    );
}

inline float AircraftRoute::calc_contribution(double distance, const User& user, uint8_t ci) {
    float multiplier = 0.0064f;
    if (distance > 10000)
        multiplier = 0.0048f;
    else if (distance > 6000)
        multiplier = 0.0032f;

    float contribution = std::min(multiplier * static_cast<float>(distance) * (3 - ci/100.0f), 152.0f);
    if (user.game_mode == User::GameMode::REALISM) contribution *= 1.5f;
    return contribution;
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

inline const string to_string(const AircraftRoute::Warning& warning) {
    switch (warning) {
        case AircraftRoute::Warning::ERR_RWY_TOO_SHORT:
            return "ERR_RWY_TOO_SHORT";
        case AircraftRoute::Warning::ERR_DISTANCE_ABOVE_SPECIFIED:
            return "ERR_DISTANCE_ABOVE_SPECIFIED";
        case AircraftRoute::Warning::ERR_DISTANCE_TOO_LONG:
            return "ERR_DISTANCE_TOO_LONG";
        case AircraftRoute::Warning::ERR_DISTANCE_TOO_SHORT:
            return "ERR_DISTANCE_TOO_SHORT";
        case AircraftRoute::Warning::REDUCED_CONTRIBUTION:
            return "REDUCED_CONTRIBUTION";
        case AircraftRoute::Warning::ERR_NO_STOPOVER:
            return "ERR_NO_STOPOVER";
        case AircraftRoute::Warning::ERR_FLIGHT_TIME_ABOVE_SPECIFIED:
            return "ERR_FLIGHT_TIME_ABOVE_SPECIFIED";
        case AircraftRoute::Warning::ERR_INSUFFICIENT_DEMAND:
            return "ERR_INSUFFICIENT_DEMAND";
        default:
            return "[UNKNOWN]";
    }
}

const string AircraftRoute::repr(const AircraftRoute& ar) {
    string s;
    if (ar.valid) {
        s = "<AircraftRoute route=" + Route::repr(ar.route);
        switch (ar._ac_type) {
            case Aircraft::Type::VIP:
            case Aircraft::Type::PAX:
                s += " config=" + Aircraft::PaxConfig::repr(get<Aircraft::PaxConfig>(ar.config));
                break;
            case Aircraft::Type::CARGO:
                s += " config=" + Aircraft::CargoConfig::repr(get<Aircraft::CargoConfig>(ar.config));
                break;
        }
        switch (ar._ac_type) {
            case Aircraft::Type::VIP:
                s += " ticket=" + VIPTicket::repr(get<VIPTicket>(ar.ticket));
                break;
            case Aircraft::Type::PAX:
                s += " ticket=" + PaxTicket::repr(get<PaxTicket>(ar.ticket));
                break;
            case Aircraft::Type::CARGO:
                s += " ticket.cargo_ticket=" + CargoTicket::repr(get<CargoTicket>(ar.ticket));
                break;
        }
        s += " max_income=" + to_string(ar.max_income) + " income=" + to_string(ar.income);
        s += " fuel=" + to_string(ar.fuel) + " co2=" + to_string(ar.co2);
        s += " needs_stopover=" + to_string(ar.needs_stopover) + " stopover=" + AircraftRoute::Stopover::repr(ar.stopover);
        s += " warnings=[";
        for (const AircraftRoute::Warning& warning : ar.warnings) {
            s += to_string(warning) + ",";
        }
        s += "]>";
    } else {
        s = "<AircraftRoute INVALID>";
    }
    return s;
}

Destination::Destination(const Airport& destination, const AircraftRoute& route) : airport(destination), ac_route(route) {}
std::vector<Destination> find_routes(const Airport& origin, const Aircraft& aircraft, const AircraftRoute::Options& options, const User& user) {
    std::vector<Destination> destinations;
    const auto& db = Database::Client();
    
    AircraftRoute::Options updated_options = options;
    updated_options.max_distance = std::min(static_cast<double>(aircraft.range * 2), options.max_distance);
    const uint16_t rwy_requirement = user.game_mode == User::GameMode::EASY ? 0 : aircraft.rwy;
    for (const Airport& ap : db->airports) {
        if (ap.rwy < rwy_requirement || ap.id == origin.id) continue;
        const AircraftRoute ar = AircraftRoute::create(origin, ap, aircraft, updated_options, user);
        if (!ar.valid) continue;
        destinations.emplace_back(ap, ar);
    }
    std::sort(destinations.begin(), destinations.end(), [](const Destination& a, const Destination& b) {
        return a.ac_route.profit > b.ac_route.profit;
    });
    return destinations;
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

py::list to_list(const vector<AircraftRoute::Warning>& warnings) {
    py::list l;
    for (const AircraftRoute::Warning& w : warnings) {
        l.append(to_string(w));
    }
    return l;
}

py::dict to_dict(const AircraftRoute& ar) {
    py::dict d(
        "route"_a = to_dict(ar.route),
        "warnings"_a = to_list(ar.warnings),
        "valid"_a = false
    );

    if (std::any_of(std::begin(ar.warnings), std::end(ar.warnings), [](const AircraftRoute::Warning& w) {
        return w == AircraftRoute::Warning::ERR_RWY_TOO_SHORT ||
            w == AircraftRoute::Warning::ERR_DISTANCE_ABOVE_SPECIFIED ||
            w == AircraftRoute::Warning::ERR_DISTANCE_TOO_LONG ||
            w == AircraftRoute::Warning::ERR_DISTANCE_TOO_SHORT;
    })) return d;

    d["needs_stopover"] = ar.needs_stopover;
    d["stopover"] = to_dict(ar.stopover);

    if (std::any_of(std::begin(ar.warnings), std::end(ar.warnings), [](const AircraftRoute::Warning& w) {
        return w == AircraftRoute::Warning::ERR_NO_STOPOVER;
    })) return d;

    d["flight_time"] = ar.flight_time;

    if (std::any_of(std::begin(ar.warnings), std::end(ar.warnings), [](const AircraftRoute::Warning& w) {
        return w == AircraftRoute::Warning::ERR_FLIGHT_TIME_ABOVE_SPECIFIED ||
            w == AircraftRoute::Warning::ERR_INSUFFICIENT_DEMAND;
    })) return d;

    d["trips_per_day"] = ar.trips_per_day;

    switch (ar._ac_type) {
        case Aircraft::Type::PAX:
            d["config"] = to_dict(get<Aircraft::PaxConfig>(ar.config));
            d["ticket"] = to_dict(get<PaxTicket>(ar.ticket));
            break;
        case Aircraft::Type::VIP:
            d["config"] = to_dict(get<Aircraft::PaxConfig>(ar.config));
            d["ticket"] = to_dict(get<VIPTicket>(ar.ticket));
            break;
        case Aircraft::Type::CARGO:
            d["config"] = to_dict(get<Aircraft::CargoConfig>(ar.config));
            d["ticket"] = to_dict(get<CargoTicket>(ar.ticket));
            break;
    }
    d["max_income"] = ar.max_income;
    d["income"] = ar.income;
    d["fuel"] = ar.fuel;
    d["co2"] = ar.co2;
    d["acheck_cost"] = ar.acheck_cost;
    d["repair_cost"] = ar.repair_cost;
    d["profit"] = ar.profit;
    d["ci"] = ar.ci;
    d["contribution"] = ar.contribution;
    
    return d;
}

py::dict to_dict(const Destination& d) {
    return py::dict(
        "airport"_a = to_dict(d.airport),
        "route"_a = to_dict(d.ac_route)
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
    
    py::class_<AircraftRoute::Options> acr_options_class(acr_class, "Options");
    py::enum_<AircraftRoute::Options::TPDMode>(acr_options_class, "TPDMode")
        .value("AUTO", AircraftRoute::Options::TPDMode::AUTO)
        .value("AUTO_MULTIPLE_OF", AircraftRoute::Options::TPDMode::AUTO_MULTIPLE_OF)
        .value("STRICT", AircraftRoute::Options::TPDMode::STRICT);
    acr_options_class
        .def(py::init<AircraftRoute::Options::TPDMode, uint16_t, double, double, AircraftRoute::Options::ConfigAlgorithm>(),
            "tpd_mode"_a = AircraftRoute::Options::TPDMode::AUTO,
            "trips_per_day"_a = 1,
            "max_distance"_a = MAX_DISTANCE,
            "max_flight_time"_a = 24.0f,
            "config_algorithm"_a = std::monostate()
        )
        .def_readwrite("tpd_mode", &AircraftRoute::Options::tpd_mode)
        .def_readwrite("trips_per_day", &AircraftRoute::Options::trips_per_day)
        .def_readwrite("max_distance", &AircraftRoute::Options::max_distance)
        .def_readwrite("max_flight_time", &AircraftRoute::Options::max_flight_time)
        .def_readwrite("config_algorithm", &AircraftRoute::Options::config_algorithm);

    py::class_<AircraftRoute::Stopover>(acr_class, "Stopover")
        .def_readonly("airport", &AircraftRoute::Stopover::airport)
        .def_readonly("full_distance", &AircraftRoute::Stopover::full_distance)
        .def_readonly("exists", &AircraftRoute::Stopover::exists)
        .def_static("find_by_efficiency", &AircraftRoute::Stopover::find_by_efficiency, "origin"_a, "destination"_a, "aircraft"_a, "game_mode"_a)
        .def("__repr__", &AircraftRoute::Stopover::repr)
        .def("to_dict", py::overload_cast<const AircraftRoute::Stopover&>(&to_dict));
    
    py::enum_<AircraftRoute::Warning>(acr_class, "Warning")
        .value("ERR_RWY_TOO_SHORT", AircraftRoute::Warning::ERR_RWY_TOO_SHORT)
        .value("ERR_DISTANCE_ABOVE_SPECIFIED", AircraftRoute::Warning::ERR_DISTANCE_ABOVE_SPECIFIED)
        .value("ERR_DISTANCE_TOO_LONG", AircraftRoute::Warning::ERR_DISTANCE_TOO_LONG)
        .value("ERR_DISTANCE_TOO_SHORT", AircraftRoute::Warning::ERR_DISTANCE_TOO_SHORT)
        .value("REDUCED_CONTRIBUTION", AircraftRoute::Warning::REDUCED_CONTRIBUTION)
        .value("ERR_NO_STOPOVER", AircraftRoute::Warning::ERR_NO_STOPOVER)
        .value("ERR_FLIGHT_TIME_ABOVE_SPECIFIED", AircraftRoute::Warning::ERR_FLIGHT_TIME_ABOVE_SPECIFIED)
        .value("ERR_INSUFFICIENT_DEMAND", AircraftRoute::Warning::ERR_INSUFFICIENT_DEMAND);

    acr_class
        .def_readonly("route", &AircraftRoute::route)
        .def_readonly("config", &AircraftRoute::config)
        .def_readonly("ticket", &AircraftRoute::ticket)
        .def_readonly("trips_per_day", &AircraftRoute::trips_per_day)
        .def_readonly("max_income", &AircraftRoute::max_income)
        .def_readonly("income", &AircraftRoute::income)
        .def_readonly("fuel", &AircraftRoute::fuel)
        .def_readonly("co2", &AircraftRoute::co2)
        .def_readonly("acheck_cost", &AircraftRoute::acheck_cost)
        .def_readonly("repair_cost", &AircraftRoute::repair_cost)
        .def_readonly("profit", &AircraftRoute::profit)
        .def_readonly("flight_time", &AircraftRoute::flight_time)
        .def_readonly("ci", &AircraftRoute::ci)
        .def_readonly("contribution", &AircraftRoute::contribution)
        .def_readonly("needs_stopover", &AircraftRoute::needs_stopover)
        .def_readonly("stopover", &AircraftRoute::stopover)
        .def_readonly("warnings", &AircraftRoute::warnings)
        .def_readonly("valid", &AircraftRoute::valid)
        .def_static("create", &AircraftRoute::create,
            "ap0"_a,
            "ap1"_a,
            "ac"_a,
            py::arg_v("options", AircraftRoute::Options(), "AircraftRoute.Options()"),
            py::arg_v("user", User::Default(), "am4utils._core.game.User.Default()")
        )
        .def_static("estimate_load", &AircraftRoute::estimate_load,
            "reputation"_a = 87,
            "autoprice_ratio"_a = 1.06,
            "has_stopover"_a = false
        )
        .def_static("calc_fuel", &AircraftRoute::calc_fuel,
            "ac"_a,
            "distance"_a,
            py::arg_v("user", User::Default(), "am4utils._core.game.User.Default()"),
            "ci"_a = 200
        )
        .def_static("calc_co2", py::overload_cast<const Aircraft&, const Aircraft::PaxConfig&, double, const User&, uint8_t>(&AircraftRoute::calc_co2),
            "ac"_a,
            "cfg"_a,
            "distance"_a,
            py::arg_v("user", User::Default(), "am4utils._core.game.User.Default()"),
            "ci"_a = 200
        )
        .def_static("calc_co2", py::overload_cast<const Aircraft&, const Aircraft::CargoConfig&, double, const User&, uint8_t>(&AircraftRoute::calc_co2),
            "ac"_a,
            "cfg"_a,
            "distance"_a,
            py::arg_v("user", User::Default(), "am4utils._core.game.User.Default()"),
            "ci"_a = 200
        )
        .def("__repr__", &AircraftRoute::repr)
        .def("to_dict", py::overload_cast<const AircraftRoute&>(&to_dict));
    
    py::class_<Destination>(m_route, "Destination")
        .def_readonly("airport", &Destination::airport)
        .def_readonly("ac_route", &Destination::ac_route)
        .def("to_dict", py::overload_cast<const Destination&>(&to_dict));

    m_route.def("find_routes", &find_routes, "ap0"_a, "ac"_a, py::arg_v("options", AircraftRoute::Options(), "AircraftRoute.Options()"), py::arg_v("user", User::Default(), "am4utils._core.game.User.Default()"));
}
#endif