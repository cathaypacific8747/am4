#include <iostream>

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
            std::ignore = std::stoi(s.substr(3));
            return Aircraft::ParseResult(Aircraft::SearchType::ID, s.substr(3));
        } catch (const std::invalid_argument&) {
        } catch (const std::out_of_range&) {
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
    string result;
    result += "<Aircraft." + to_string(ac.id) + "." + to_string(ac.eid) + " shortname=" + ac.shortname;
    result += " fuel=" + to_string(ac.fuel) + " co2=" + to_string(ac.co2) + " $" + to_string(ac.cost) + " rng=" + to_string(ac.range) + ">";
    return result;
}


// PURCHASED AIRCRAFT
PaxConfig PaxConfig::calc_fjy_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.f = d_pf.f * 3 > capacity ? capacity / 3 : d_pf.f;
    config.j = d_pf.f * 3 + d_pf.j * 2 > capacity ? (capacity - config.f * 3) / 2 : d_pf.j;
    config.y = capacity - config.f * 3 - config.j * 2;
    config.valid = config.y < d_pf.y;
    config.algorithm = PaxConfig::Algorithm::FJY;
    return config;
};

PaxConfig PaxConfig::calc_fyj_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.f = d_pf.f * 3 > capacity ? capacity / 3 : d_pf.f;
    config.y = d_pf.f * 3 + d_pf.y > capacity ? capacity - config.f * 3 : d_pf.y;
    config.j = (capacity - config.f * 3 - config.y) / 2;
    config.valid = config.j < d_pf.j;
    config.algorithm = PaxConfig::Algorithm::FYJ;
    return config;
};

PaxConfig PaxConfig::calc_jfy_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.j = d_pf.j * 2 > capacity ? capacity / 2 : d_pf.j;
    config.f = d_pf.j * 2 + d_pf.f * 3 > capacity ? (capacity - config.j * 2) / 3 : d_pf.f;
    config.y = capacity - config.j * 2 - config.f * 3;
    config.valid = config.y < d_pf.y;
    config.algorithm = PaxConfig::Algorithm::JFY;
    return config;
};

PaxConfig PaxConfig::calc_jyf_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.j = d_pf.j * 2 > capacity ? capacity / 2 : d_pf.j;
    config.y = d_pf.j * 2 + d_pf.y > capacity ? capacity - config.j * 2 : d_pf.y;
    config.f = capacity - config.y - config.j * 2;
    config.valid = config.f < d_pf.f;
    config.algorithm = PaxConfig::Algorithm::JYF;
    return config;
};

PaxConfig PaxConfig::calc_yfj_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.y = d_pf.y > capacity ? capacity : d_pf.y;
    config.f = d_pf.y + d_pf.f * 3 > capacity ? (capacity - config.y) / 3 : d_pf.f;
    config.j = (capacity - config.y - config.f * 3) / 2;
    config.valid = config.j < d_pf.j;
    config.algorithm = PaxConfig::Algorithm::YFJ;
    return config;
};

PaxConfig PaxConfig::calc_yjf_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.y = d_pf.y > capacity ? capacity : d_pf.y;
    config.j = d_pf.y + d_pf.j * 2 > capacity ? (capacity - config.y) / 2 : d_pf.j;
    config.f = capacity - config.y - config.j * 2;
    config.valid = config.f < d_pf.f;
    config.algorithm = PaxConfig::Algorithm::YJF;
    return config;
};

PaxConfig PaxConfig::calc_pax_conf(const PaxDemand& d_pf, uint16_t capacity, double distance, User::GameMode game_mode) {
    if (game_mode == User::GameMode::EASY) {
        if (distance < 14425) {
            return calc_fjy_conf(d_pf, capacity);
        } else if (distance < 14812.5) {
            return calc_fyj_conf(d_pf, capacity);
        } else if (distance < 15200) {
            return calc_yfj_conf(d_pf, capacity);
        } else {
            return calc_yjf_conf(d_pf, capacity);
        }
    } else {
        if (distance < 13888.8888) {
            return calc_fjy_conf(d_pf, capacity);
        } else if (distance < 15694.4444) {
            return calc_jfy_conf(d_pf, capacity);
        } else if (distance < 17500) {
            return calc_jyf_conf(d_pf, capacity);
        } else {
            return calc_yjf_conf(d_pf, capacity);
        }
    }
}

const string PaxConfig::repr(const PaxConfig& config) {
    return "<PaxConfig " + to_string(config.y) + "|" + to_string(config.j) + "|" + to_string(config.f) + ">";
}


CargoConfig CargoConfig::calc_l_conf(const CargoDemand& d_pf, uint32_t capacity) {
    double l_cap = capacity * 0.7;

    CargoConfig config;
    if (d_pf.l > l_cap) {
        config.l = 100;
        config.h = 0;
        config.valid = true;
    } else {
        config.l = static_cast<uint8_t>(d_pf.l / l_cap * 100);
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
        config.h = static_cast<uint8_t>(d_pf.h / capacity * 100);
        config.l = 100 - config.h;
        config.valid = d_pf.l >= capacity - d_pf.h;
    }
    config.algorithm = CargoConfig::Algorithm::H;
    return config;
}

CargoConfig CargoConfig::calc_cargo_conf(const CargoDemand& d_pf, uint32_t capacity, uint8_t l_training) {
    return calc_l_conf(
        d_pf,
        static_cast<uint32_t>(capacity * (1 + l_training / 100.0))
    ); // low priority is always more profitable
}

const string CargoConfig::repr(const CargoConfig& config) {
    return "<CargoConfig " + to_string(config.l) + "|" + to_string(config.h) + ">";
}


const string PurchasedAircraft::repr(const PurchasedAircraft& ac) {
    string result;
    result += "<PurchasedAircraft." + to_string(ac.id) + "." + to_string(ac.eid) + " shortname=" + ac.shortname;
    switch (ac.type) {
        case Aircraft::Type::VIP:
        case Aircraft::Type::PAX:
            result += " config.pax_config=" + PaxConfig::repr(ac.config.pax_config);
            break;
        case Aircraft::Type::CARGO:
            result += " config.cargo_config=" + CargoConfig::repr(ac.config.cargo_config);
            break;
    }
    
    result += " fuel=" + to_string(ac.fuel) + " co2=" + to_string(ac.co2) + " $" + to_string(ac.cost) + " rng=" + to_string(ac.range) + ">";
    return result;
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

void pybind_init_aircraft(py::module_& m) {
    py::module_ m_ac = m.def_submodule("aircraft");
    
    py::class_<Aircraft, shared_ptr<Aircraft>> ac_class(m_ac, "Aircraft");
    py::enum_<Aircraft::Type>(ac_class, "Type")
        .value("PAX", Aircraft::Type::PAX)
        .value("CARGO", Aircraft::Type::CARGO)
        .value("VIP", Aircraft::Type::VIP);
    ac_class
        .def_readonly("id", &Aircraft::id)
        .def_readonly("shortname", &Aircraft::shortname)
        .def_readonly("manufacturer", &Aircraft::manufacturer)
        .def_readonly("name", &Aircraft::name)
        .def_readonly("type", &Aircraft::type)
        .def_readonly("priority", &Aircraft::priority)
        .def_readonly("eid", &Aircraft::eid)
        .def_readonly("ename", &Aircraft::ename)
        .def_readonly("speed", &Aircraft::speed)
        .def_readonly("fuel", &Aircraft::fuel)
        .def_readonly("co2", &Aircraft::co2)
        .def_readonly("cost", &Aircraft::cost)
        .def_readonly("capacity", &Aircraft::capacity)
        .def_readonly("rwy", &Aircraft::rwy)
        .def_readonly("check_cost", &Aircraft::check_cost)
        .def_readonly("range", &Aircraft::range)
        .def_readonly("ceil", &Aircraft::ceil)
        .def_readonly("maint", &Aircraft::maint)
        .def_readonly("pilots", &Aircraft::pilots)
        .def_readonly("crew", &Aircraft::crew)
        .def_readonly("engineers", &Aircraft::engineers)
        .def_readonly("technicians", &Aircraft::technicians)
        .def_readonly("img", &Aircraft::img)
        .def_readonly("wingspan", &Aircraft::wingspan)
        .def_readonly("length", &Aircraft::length)
        .def_readonly("valid", &Aircraft::valid)
        .def("__repr__", &Aircraft::repr);
    py::enum_<Aircraft::SearchType>(ac_class, "SearchType")
        .value("ALL", Aircraft::SearchType::ALL)
        .value("ID", Aircraft::SearchType::ID)
        .value("SHORTNAME", Aircraft::SearchType::SHORTNAME)
        .value("NAME", Aircraft::SearchType::NAME);
    py::class_<Aircraft::ParseResult>(ac_class, "ParseResult")
        .def(py::init<Aircraft::SearchType, const string&>())
        .def_readonly("search_type", &Aircraft::ParseResult::search_type)
        .def_readonly("search_str", &Aircraft::ParseResult::search_str);
    py::class_<Aircraft::SearchResult>(ac_class, "SearchResult")
        .def(py::init<shared_ptr<Aircraft>, Aircraft::ParseResult>())
        .def_readonly("ac", &Aircraft::SearchResult::ac)
        .def_readonly("parse_result", &Aircraft::SearchResult::parse_result);
    py::class_<Aircraft::Suggestion>(ac_class, "Suggestion")
        .def(py::init<shared_ptr<Aircraft>, double>())
        .def_readonly("ac", &Aircraft::Suggestion::ac)
        .def_readonly("score", &Aircraft::Suggestion::score);
    ac_class
        .def_static("search", &Aircraft::search, "s"_a)
        .def_static("suggest", &Aircraft::suggest, "s"_a);
    
    // puchased aircraft
    py::class_<PaxConfig> pc_class(m_ac, "PaxConfig");
    py::enum_<PaxConfig::Algorithm>(pc_class, "Algorithm")
        .value("FJY", PaxConfig::Algorithm::FJY).value("FYJ", PaxConfig::Algorithm::FYJ)
        .value("JFY", PaxConfig::Algorithm::JFY).value("JYF", PaxConfig::Algorithm::JYF)
        .value("YJF", PaxConfig::Algorithm::YJF).value("YFJ", PaxConfig::Algorithm::YFJ)
        .value("NONE", PaxConfig::Algorithm::NONE);
    pc_class
        .def_readonly("y", &PaxConfig::y)
        .def_readonly("j", &PaxConfig::j)
        .def_readonly("f", &PaxConfig::f)
        .def_readonly("valid", &PaxConfig::valid)
        .def_readonly("algorithm", &PaxConfig::algorithm)
        .def("__repr__", &PaxConfig::repr);

    py::class_<CargoConfig> cc_class(m_ac, "CargoConfig");
    py::enum_<CargoConfig::Algorithm>(cc_class, "Algorithm")
        .value("L", CargoConfig::Algorithm::L).value("H", CargoConfig::Algorithm::H)
        .value("NONE", CargoConfig::Algorithm::NONE);
    cc_class
        .def_readonly("l", &CargoConfig::l)
        .def_readonly("h", &CargoConfig::h)
        .def_readonly("valid", &CargoConfig::valid)
        .def_readonly("algorithm", &CargoConfig::algorithm)
        .def("__repr__", &CargoConfig::repr);

    py::class_<PurchasedAircraft, shared_ptr<PurchasedAircraft>, Aircraft> p_ac_class(m_ac, "PurchasedAircraft");
    py::class_<PurchasedAircraft::Config>(p_ac_class, "Config")
        .def_readonly("pax_config", &PurchasedAircraft::Config::pax_config)
        .def_readonly("cargo_config", &PurchasedAircraft::Config::cargo_config);
    p_ac_class
        .def_readonly("config", &PurchasedAircraft::config)
        .def("__repr__", &PurchasedAircraft::repr);
}
#endif