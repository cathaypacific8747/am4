#include <iostream>
#include <sstream>

#include "include/db.hpp"
#include "include/aircraft.hpp"

Aircraft::Aircraft() : valid(false) {}

Aircraft::ParseResult Aircraft::parse(const string& s) {
    string s_lower = s;
    std::transform(s_lower.begin(), s_lower.end(), s_lower.begin(), ::tolower);

    if (s_lower.substr(0, 5) == "name:") {
        return Aircraft::ParseResult(Aircraft::SearchType::NAME, s_lower.substr(5));
    } else if (s_lower.substr(0, 10) == "shortname:") {
        return Aircraft::ParseResult(Aircraft::SearchType::SHORTNAME, s_lower.substr(10));
    } else if (s_lower.substr(0, 3) == "id:") {
        try {
            uint16_t id = std::stoi(s.substr(3));
            return Aircraft::ParseResult(Aircraft::SearchType::ID, s.substr(3));
        } catch (std::invalid_argument& e) {
        } catch (std::out_of_range& e) {
        }
    } else if (s_lower.substr(0, 4) == "all:") {
        return Aircraft::ParseResult(Aircraft::SearchType::ALL, s_lower.substr(4));
    }
    return Aircraft::ParseResult(Aircraft::SearchType::ALL, s_lower);
}

Aircraft::SearchResult Aircraft::search(const string& s) {
    auto parse_result = Aircraft::ParseResult(Aircraft::parse(s));
    int8_t priority = 0; // TODO: attempt to parse engine type!
    duckdb::unique_ptr<duckdb::QueryResult> result;
    switch (parse_result.search_type) {
        case Aircraft::SearchType::ALL:
            result = Database::Client()->get_aircraft_by_all->Execute(parse_result.search_str.c_str(), priority);
            break;
        case Aircraft::SearchType::NAME:
            result = Database::Client()->get_aircraft_by_name->Execute(parse_result.search_str.c_str(), priority);
            break;
        case Aircraft::SearchType::SHORTNAME:
            result = Database::Client()->get_aircraft_by_shortname->Execute(parse_result.search_str.c_str(), priority);
            break;
        case Aircraft::SearchType::ID:
            result = Database::Client()->get_aircraft_by_id->Execute(std::stoi(parse_result.search_str), priority);
            break;
    }
    CHECK_SUCCESS(result);
    duckdb::unique_ptr<duckdb::DataChunk> chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Aircraft::SearchResult(make_shared<Aircraft>(), parse_result);

    return Aircraft::SearchResult(make_shared<Aircraft>(chunk, 0), parse_result);
}

std::vector<Aircraft::Suggestion> Aircraft::suggest(const ParseResult& parse_result) {
    std::vector<Aircraft::Suggestion> suggestions;
    int8_t priority = 0; // TODO: attempt to parse engine type!
    if (parse_result.search_type == Aircraft::SearchType::ALL) {
        for (auto& stmt : {
            Database::Client()->suggest_aircraft_by_shortname.get(),
            Database::Client()->suggest_aircraft_by_name.get(),
        }) {
            auto result = stmt->Execute(parse_result.search_str.c_str(), priority);
            CHECK_SUCCESS(result);
            auto chunk = result->Fetch();
            if (!chunk || chunk->size() == 0) continue;

            for (idx_t i = 0; i < chunk->size(); i++) {
                suggestions.emplace_back(
                    make_shared<Aircraft>(chunk, i),
                    chunk->GetValue(25, i).GetValue<double>()
                );
            }
        }
        std::partial_sort(suggestions.begin(), suggestions.begin() + 5, suggestions.end(), [](const Aircraft::Suggestion& a, const Aircraft::Suggestion& b) {
            return a.score > b.score;
        });
        suggestions.resize(5);
    } else {
        duckdb::unique_ptr<duckdb::QueryResult> result;
        switch (parse_result.search_type) {
            case Aircraft::SearchType::NAME:
                result = Database::Client()->suggest_aircraft_by_name->Execute(parse_result.search_str.c_str(), priority);
                break;
            case Aircraft::SearchType::SHORTNAME:
                result = Database::Client()->suggest_aircraft_by_shortname->Execute(parse_result.search_str.c_str(), priority);
                break;
        }
        CHECK_SUCCESS(result);
        while (auto chunk = result->Fetch()) {
            for (idx_t i = 0; i < chunk->size(); i++) {
                suggestions.emplace_back(
                    make_shared<Aircraft>(chunk, i),
                    chunk->GetValue(25, i).GetValue<double>()
                );
            }
        }
    }
    return suggestions;
}

Aircraft::Aircraft(const duckdb::unique_ptr<duckdb::DataChunk>& chunk, idx_t row) : 
    id(chunk->GetValue(0, row).GetValue<uint16_t>()),
    shortname(chunk->GetValue(1, row).GetValue<string>()),
    manufacturer(chunk->GetValue(2, row).GetValue<string>()),
    name(chunk->GetValue(3, row).GetValue<string>()),
    type(static_cast<Aircraft::Type>(chunk->GetValue(4, row).GetValue<uint8_t>())),
    priority(chunk->GetValue(5, row).GetValue<uint8_t>()),
    eid(chunk->GetValue(6, row).GetValue<uint16_t>()),
    ename(chunk->GetValue(7, row).GetValue<string>()),
    speed(chunk->GetValue(8, row).GetValue<float>()),
    fuel(chunk->GetValue(9, row).GetValue<float>()),
    co2(chunk->GetValue(10, row).GetValue<float>()),
    cost(chunk->GetValue(11, row).GetValue<uint32_t>()),
    capacity(chunk->GetValue(12, row).GetValue<uint32_t>()),
    rwy(chunk->GetValue(13, row).GetValue<uint16_t>()),
    check_cost(chunk->GetValue(14, row).GetValue<uint32_t>()),
    range(chunk->GetValue(15, row).GetValue<uint16_t>()),
    ceil(chunk->GetValue(16, row).GetValue<uint16_t>()),
    maint(chunk->GetValue(17, row).GetValue<uint16_t>()),
    pilots(chunk->GetValue(18, row).GetValue<uint8_t>()),
    crew(chunk->GetValue(19, row).GetValue<uint8_t>()),
    engineers(chunk->GetValue(20, row).GetValue<uint8_t>()),
    technicians(chunk->GetValue(21, row).GetValue<uint8_t>()),
    img(chunk->GetValue(22, row).GetValue<string>()),
    wingspan(chunk->GetValue(23, row).GetValue<uint8_t>()),
    length(chunk->GetValue(24, row).GetValue<uint8_t>()),
    valid(true)
{};

const string to_string(Aircraft::Type type) {
    switch(type) {
        case Aircraft::Type::PAX:
            return "PAX";
        case Aircraft::Type::CARGO:
            return "CARGO";
        case Aircraft::Type::VIP:
            return "VIP";
        default:
            return "[UNKNOWN]";
    }
}

const string to_string(Aircraft::SearchType searchtype) {
    switch (searchtype) {
        case Aircraft::SearchType::ALL:
            return "ALL";
        case Aircraft::SearchType::ID:
            return "ID";
        case Aircraft::SearchType::SHORTNAME:
            return "SHORTNAME";
        case Aircraft::SearchType::NAME:
            return "NAME";
        default:
            return "[UNKNOWN]";
    }
}

const string Aircraft::repr(const Aircraft& ac) {
    std::stringstream ss;
    ss << "<Aircraft." << ac.id << "." << ac.eid << " " << ac.shortname << " '" << ac.manufacturer << " " << ac.name << "' " << to_string(ac.type);
    ss << " f" << ac.fuel << " c" << ac.co2 << " $" << ac.cost << " R" << ac.range << ">";
    return ss.str();
}


// PURCHASED AIRCRAFT
PaxConfig PaxConfig::calc_fjy_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.f = d_pf.f * 3 > capacity ? capacity / 3 : d_pf.f;
    config.j = d_pf.f * 3 + d_pf.j * 2 > capacity ? (capacity - config.f * 3) / 2 : d_pf.j;
    config.y = capacity - config.f * 3 - config.j * 2;
    config.valid = config.y < d_pf.y;
    config.algorithm = PaxConfig::Algorithm::FJY;
    return config;
};

PaxConfig PaxConfig::calc_fyj_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.f = d_pf.f * 3 > capacity ? capacity / 3 : d_pf.f;
    config.y = d_pf.f * 3 + d_pf.y > capacity ? capacity - config.f * 3 : d_pf.y;
    config.j = (capacity - config.f * 3 - config.y) / 2;
    config.valid = config.j < d_pf.j;
    config.algorithm = PaxConfig::Algorithm::FYJ;
    return config;
};

PaxConfig PaxConfig::calc_jfy_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.j = d_pf.j * 2 > capacity ? capacity / 2 : d_pf.j;
    config.f = d_pf.j * 2 + d_pf.f * 3 > capacity ? (capacity - config.j * 2) / 3 : d_pf.f;
    config.y = capacity - config.j * 2 - config.f * 3;
    config.valid = config.y < d_pf.y;
    config.algorithm = PaxConfig::Algorithm::JFY;
    return config;
};

PaxConfig PaxConfig::calc_jyf_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.j = d_pf.j * 2 > capacity ? capacity / 2 : d_pf.j;
    config.y = d_pf.j * 2 + d_pf.y > capacity ? capacity - config.j * 2 : d_pf.y;
    config.f = capacity - config.y - config.j * 2;
    config.valid = config.f < d_pf.f;
    config.algorithm = PaxConfig::Algorithm::JYF;
    return config;
};

PaxConfig PaxConfig::calc_yfj_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.y = d_pf.y > capacity ? capacity : d_pf.y;
    config.f = d_pf.y + d_pf.f * 3 > capacity ? (capacity - config.y) / 3 : d_pf.f;
    config.j = (capacity - config.y - config.f * 3) / 2;
    config.valid = config.j < d_pf.j;
    config.algorithm = PaxConfig::Algorithm::YFJ;
    return config;
};

PaxConfig PaxConfig::calc_yjf_conf(const PaxDemand& d_pf, uint16_t capacity, float distance) {
    PaxConfig config;
    config.y = d_pf.y > capacity ? capacity : d_pf.y;
    config.j = d_pf.y + d_pf.j * 2 > capacity ? (capacity - config.y) / 2 : d_pf.j;
    config.f = capacity - config.y - config.j * 2;
    config.valid = config.f < d_pf.f;
    config.algorithm = PaxConfig::Algorithm::YJF;
    return config;
};

PaxConfig PaxConfig::calc_pax_conf(const PaxDemand& pax_demand, uint16_t capacity, float distance, uint16_t trips_per_day, User::GameMode game_mode) {
    PaxDemand d_pf = PaxDemand(
        pax_demand.y / trips_per_day,
        pax_demand.j / trips_per_day,
        pax_demand.f / trips_per_day
    );

    PaxConfig config;
    if (game_mode == User::GameMode::EASY) {
        if (distance < 14425) {
            config = calc_fjy_conf(d_pf, capacity, distance);
        } else if (distance < 14812.5) {
            config = calc_fyj_conf(d_pf, capacity, distance);
        } else if (distance < 15200) {
            config = calc_yfj_conf(d_pf, capacity, distance);
        } else {
            config = calc_yjf_conf(d_pf, capacity, distance);
        }
    } else {
        if (distance < 13888.8888) {
            config = calc_fjy_conf(d_pf, capacity, distance);
        } else if (distance < 15694.4444) {
            config = calc_jfy_conf(d_pf, capacity, distance);
        } else if (distance < 17500) {
            config = calc_jyf_conf(d_pf, capacity, distance);
        } else {
            config = calc_yjf_conf(d_pf, capacity, distance);
        }
    }
    return config;
}


CargoConfig CargoConfig::calc_l_conf(const CargoDemand& d_pf, uint32_t capacity) {
    double l_cap = capacity * 0.7;

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
    config.algorithm = CargoConfig::Algorithm::L;
    return config;
}

// virually useless, never profitable unless distance > ~23000 km
CargoConfig CargoConfig::calc_h_conf(const CargoDemand& d_pf, uint32_t capacity) {
    CargoConfig config;
    if (d_pf.h > capacity) {
        config.h = 100;
        config.l = 0;
        config.valid = true;
    } else {
        config.h = d_pf.h / capacity * 100;
        config.l = 100 - config.h;
        config.valid = d_pf.l >= capacity - d_pf.h;
    }
    config.algorithm = CargoConfig::Algorithm::H;
    return config;
}

CargoConfig CargoConfig::calc_cargo_conf(const CargoDemand& cargo_demand, uint32_t capacity, uint16_t trips_per_day, uint8_t l_training) {
    CargoDemand d_pf = CargoDemand(
        cargo_demand.l / trips_per_day,
        cargo_demand.h / trips_per_day
    );
    double true_capacity = capacity * (1 + l_training / 100.0);

    return calc_l_conf(d_pf, true_capacity); // low priority is always more profitable
}

const string PurchasedAircraft::repr(const PurchasedAircraft& ac) {
    std::stringstream ss;
    std::string actype = to_string(ac.type);
    ss << "<PurchasedAircraft." << ac.id << "." << ac.eid << " " << ac.shortname << " '" << ac.manufacturer << " " << ac.name << "' " << actype;
    ss << " f" << ac.fuel << " c" << ac.co2 << " $" << ac.cost << " R" << ac.range << ">";

    return ss.str();
}