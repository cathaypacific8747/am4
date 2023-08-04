#include <iostream>
#include <algorithm>
#include <string>

#include "include/db.hpp"
#include "include/aircraft.hpp"

Aircraft::Aircraft() : speed_mod(false), fuel_mod(false), co2_mod(false), fourx_mod(false), valid(false) {}

// removes trailing spaces or spaces that suceed commas in-place
void remove_spaces_custom(string& str) {
    bool space_found = false;
    size_t len = str.length();

    for (size_t i = 0; i < len; i++) {
        if (str[i] == ' ' && ((i == 0 || i == len - 1 || str[i-1] == ',') || space_found)) {
            space_found = true;
            str.erase(i, 1);
            i--;
            len--;
        } else {
            space_found = false;
        }
    }
}

Aircraft::ParseResult Aircraft::parse(const string& s) {
    string s_lower = s;
    std::transform(s_lower.begin(), s_lower.end(), s_lower.begin(), ::tolower);

    uint8_t priority = 0;
    bool speed_mod = false;
    bool fuel_mod = false;
    bool co2_mod = false;

    // attempt to get modifiers, e.g. mc214[0,s,c,f] -> priority: true, speed_mod: true, co2_mod: true, fuel_mod: true
    size_t start = s_lower.find('[');
    if (start != string::npos && s_lower.at(s_lower.size() - 1) == ']') {
        string parsed = s_lower.substr(start + 1, s_lower.size() - start - 2);
        remove_spaces_custom(parsed);
        s_lower = s_lower.substr(0, start);

        std::vector<string> tokens;
        size_t last = 0, next = 0;
        while ((next = parsed.find(',', last)) != string::npos) {
            tokens.push_back(parsed.substr(last, next-last));
            last = next + 1;
        }
        tokens.push_back(parsed.substr(last));

        for (const string& token : tokens) {
            if (token.length() <= 3) {
                if (token.find('s') != string::npos) speed_mod = true;
                if (token.find('f') != string::npos) fuel_mod = true;
                if (token.find('c') != string::npos) co2_mod = true;
            }
            try {
                if (priority == 0) priority = static_cast<uint8_t>(std::stoi(token));
            } catch (const std::invalid_argument&) {
            } catch (const std::out_of_range&) {
            }
        }
    }
    if (s_lower.substr(0, 5) == "name:") {
        return Aircraft::ParseResult(Aircraft::SearchType::NAME, s_lower.substr(5), priority, speed_mod, fuel_mod, co2_mod);
    } else if (s_lower.substr(0, 10) == "shortname:") {
        return Aircraft::ParseResult(Aircraft::SearchType::SHORTNAME, s_lower.substr(10), priority, speed_mod, fuel_mod, co2_mod);
    } else if (s_lower.substr(0, 3) == "id:") {
        try {
            std::ignore = std::stoi(s.substr(3));
            return Aircraft::ParseResult(Aircraft::SearchType::ID, s.substr(3), priority, speed_mod, fuel_mod, co2_mod);
        } catch (const std::invalid_argument&) {
        } catch (const std::out_of_range&) {
        }
    } else if (s_lower.substr(0, 4) == "all:") {
        return Aircraft::ParseResult(Aircraft::SearchType::ALL, s_lower.substr(4), priority, speed_mod, fuel_mod, co2_mod);
    }
    return Aircraft::ParseResult(Aircraft::SearchType::ALL, s_lower, priority, speed_mod, fuel_mod, co2_mod);
}

Aircraft::SearchResult Aircraft::search(const string& s, const User& user) {
    auto parse_result = Aircraft::parse(s);
    Aircraft ac;
    switch (parse_result.search_type) {
        case Aircraft::SearchType::ALL:
            ac = Database::Client()->get_aircraft_by_all(parse_result.search_str, parse_result.priority);
            break;
        case Aircraft::SearchType::NAME:
            ac = Database::Client()->get_aircraft_by_name(parse_result.search_str, parse_result.priority);
            break;
        case Aircraft::SearchType::SHORTNAME:
            ac = Database::Client()->get_aircraft_by_shortname(parse_result.search_str, parse_result.priority);
            break;
        case Aircraft::SearchType::ID:
            ac = Database::Client()->get_aircraft_by_id(static_cast<uint16_t>(std::stoi(parse_result.search_str)), parse_result.priority);
            break;
    }
    ac.speed_mod = parse_result.speed_mod;
    if (ac.speed_mod) ac.speed *= 1.1f;

    ac.fuel_mod = parse_result.fuel_mod;
    if (ac.fuel_mod) ac.fuel *= 0.9f;
    
    ac.co2_mod = parse_result.co2_mod;
    if (ac.co2_mod) ac.co2 *= 0.9f;

    ac.fourx_mod = user.fourx;
    if (ac.fourx_mod) ac.speed *= 4.0f;
    
    return Aircraft::SearchResult(make_shared<Aircraft>(ac), parse_result);
}

std::vector<Aircraft::Suggestion> Aircraft::suggest(const ParseResult& parse_result) {
    std::vector<Aircraft::Suggestion> suggestions;
    switch (parse_result.search_type) {
        case Aircraft::SearchType::ALL:
            suggestions = Database::Client()->suggest_aircraft_by_all(parse_result.search_str);
            break;
        case Aircraft::SearchType::NAME:
            suggestions = Database::Client()->suggest_aircraft_by_name(parse_result.search_str);
            break;
        case Aircraft::SearchType::SHORTNAME:
            suggestions = Database::Client()->suggest_aircraft_by_shortname(parse_result.search_str);
            break;
        default:
            return suggestions;
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
    speed_mod(false),
    fuel_mod(false),
    co2_mod(false),
    fourx_mod(false),
    valid(true)
{};

inline const string to_string(Aircraft::Type type) {
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

inline const string to_string(Aircraft::SearchType searchtype) {
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
    if (!ac.valid) return "<Aircraft.INVALID>";
    string result;
    result += "<Aircraft." + to_string(ac.id) + "." + to_string(ac.eid) + " shortname=" + ac.shortname + " name=" + ac.name + " priority=" + to_string(ac.priority);
    result += " mod=";
    if (ac.speed_mod) result += "s";
    if (ac.fuel_mod) result += "f";
    if (ac.co2_mod) result += "c";
    result += " speed=" + to_string(ac.speed) + " fuel=" + to_string(ac.fuel) + " co2=" + to_string(ac.co2) + " $" + to_string(ac.cost) + " rng=" + to_string(ac.range) + ">";
    return result;
}

// test
Aircraft::PaxConfig Aircraft::PaxConfig::calc_fjy_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.f = std::min(d_pf.f, static_cast<uint16_t>(capacity / 3));
    config.j = std::min(d_pf.j, static_cast<uint16_t>((capacity - config.f * 3) / 2));
    config.y = static_cast<uint16_t>(capacity - config.f * 3 - config.j * 2);
    config.valid = config.y < d_pf.y;
    config.algorithm = PaxConfig::Algorithm::FJY;
    return config;
};

Aircraft::PaxConfig Aircraft::PaxConfig::calc_fyj_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.f = std::min(d_pf.f, static_cast<uint16_t>(capacity / 3));
    config.y = std::min(d_pf.y, static_cast<uint16_t>(capacity - config.f * 3));
    config.j = static_cast<uint16_t>((capacity - config.f * 3 - config.y) / 2);
    config.valid = config.j < d_pf.j;
    config.algorithm = PaxConfig::Algorithm::FYJ;
    return config;
};

Aircraft::PaxConfig Aircraft::PaxConfig::calc_jfy_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.j = std::min(d_pf.j, static_cast<uint16_t>(capacity / 2));
    config.f = std::min(d_pf.f, static_cast<uint16_t>((capacity - config.j * 2) / 3));
    config.y = static_cast<uint16_t>(capacity - config.j * 2 - config.f * 3);
    config.valid = config.y < d_pf.y;
    config.algorithm = PaxConfig::Algorithm::JFY;
    return config;
};

Aircraft::PaxConfig Aircraft::PaxConfig::calc_jyf_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.j = std::min(d_pf.j, static_cast<uint16_t>(capacity / 2));
    config.y = std::min(d_pf.y, static_cast<uint16_t>(capacity - config.j * 2));
    config.f = static_cast<uint16_t>(capacity - config.y - config.j * 2);
    config.valid = config.f < d_pf.f;
    config.algorithm = PaxConfig::Algorithm::JYF;
    return config;
};

Aircraft::PaxConfig Aircraft::PaxConfig::calc_yfj_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.y = std::min(d_pf.y, static_cast<uint16_t>(capacity));
    config.f = std::min(d_pf.f, static_cast<uint16_t>((capacity - config.y) / 3));
    config.j = static_cast<uint16_t>((capacity - config.y - config.f * 3) / 2);
    config.valid = config.j < d_pf.j;
    config.algorithm = PaxConfig::Algorithm::YFJ;
    return config;
};

Aircraft::PaxConfig Aircraft::PaxConfig::calc_yjf_conf(const PaxDemand& d_pf, uint16_t capacity) {
    PaxConfig config;
    config.y = std::min(d_pf.y, static_cast<uint16_t>(capacity));
    config.j = std::min(d_pf.j, static_cast<uint16_t>((capacity - config.y) / 2));
    config.f = static_cast<uint16_t>(capacity - config.y - config.j * 2);
    config.valid = config.f < d_pf.f;
    config.algorithm = PaxConfig::Algorithm::YJF;
    return config;
};

Aircraft::PaxConfig Aircraft::PaxConfig::calc_pax_conf(const PaxDemand& d_pf, uint16_t capacity, double distance, User::GameMode game_mode, Aircraft::PaxConfig::Algorithm algorithm) {
    switch (algorithm) {
        case Aircraft::PaxConfig::Algorithm::AUTO:
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
        case Aircraft::PaxConfig::Algorithm::FJY:
            return calc_fjy_conf(d_pf, capacity);
        case Aircraft::PaxConfig::Algorithm::FYJ:
            return calc_fyj_conf(d_pf, capacity);
        case Aircraft::PaxConfig::Algorithm::JFY:
            return calc_jfy_conf(d_pf, capacity);
        case Aircraft::PaxConfig::Algorithm::JYF:
            return calc_jyf_conf(d_pf, capacity);
        case Aircraft::PaxConfig::Algorithm::YFJ:
            return calc_yfj_conf(d_pf, capacity);
        case Aircraft::PaxConfig::Algorithm::YJF:
            return calc_yjf_conf(d_pf, capacity);
        default:
            return PaxConfig();
    }
}

inline const string to_string(Aircraft::PaxConfig::Algorithm algorithm) {
    switch (algorithm) {
        case Aircraft::PaxConfig::Algorithm::AUTO:
            return "AUTO";
        case Aircraft::PaxConfig::Algorithm::FJY:
            return "FJY";
        case Aircraft::PaxConfig::Algorithm::FYJ:
            return "FYJ";
        case Aircraft::PaxConfig::Algorithm::JFY:
            return "JFY";
        case Aircraft::PaxConfig::Algorithm::JYF:
            return "JYF";
        case Aircraft::PaxConfig::Algorithm::YFJ:
            return "YFJ";
        case Aircraft::PaxConfig::Algorithm::YJF:
            return "YJF";
        default:
            return "UNKNOWN";
    }
}

const string Aircraft::PaxConfig::repr(const Aircraft::PaxConfig& config) {
    return "<PaxConfig " + to_string(config.y) + "|" + to_string(config.j) + "|" + to_string(config.f) + ">";
}


Aircraft::CargoConfig Aircraft::CargoConfig::calc_l_conf(const CargoDemand& d_pf, uint32_t capacity, uint8_t l_training, uint8_t h_training) {
    double l_cap = capacity * 0.7 * (1 + l_training / 100.0);

    CargoConfig config;
    if (d_pf.l > l_cap) {
        config.l = 100;
        config.h = 0;
        config.valid = true;
    } else {
        config.l = static_cast<uint8_t>(d_pf.l / l_cap * 100);
        config.h = 100 - config.l;
        config.valid = d_pf.h >= capacity * (config.h / 100.0) * (1 + h_training / 100.0);
    }
    config.algorithm = CargoConfig::Algorithm::L;
    return config;
}

// virually useless, never profitable unless distance > ~23000 km
Aircraft::CargoConfig Aircraft::CargoConfig::calc_h_conf(const CargoDemand& d_pf, uint32_t capacity, uint8_t l_training, uint8_t h_training) {
    double h_cap = capacity * (1 + h_training / 100.0);
    
    CargoConfig config;
    if (d_pf.h > h_cap) {
        config.h = 100;
        config.l = 0;
        config.valid = true;
    } else {
        config.h = static_cast<uint8_t>(d_pf.h / h_cap * 100);
        config.l = 100 - config.h;
        config.valid = d_pf.l >= capacity * (config.l / 100.0) * 0.7 * (1 + l_training / 100.0);
    }
    config.algorithm = CargoConfig::Algorithm::H;
    return config;
}

Aircraft::CargoConfig Aircraft::CargoConfig::calc_cargo_conf(const CargoDemand& d_pf, uint32_t capacity, uint8_t l_training, uint8_t h_training, Aircraft::CargoConfig::Algorithm algorithm) {
    // low priority is always more profitable
    switch (algorithm) {
        case Aircraft::CargoConfig::Algorithm::AUTO:
        case Aircraft::CargoConfig::Algorithm::L:
            return calc_l_conf(
                d_pf,
                capacity,
                l_training,
                h_training
            ); 
        case Aircraft::CargoConfig::Algorithm::H:
            return calc_h_conf(
                d_pf,
                capacity,
                l_training,
                h_training
            );
        default:
            return CargoConfig();
    }
}  

inline const string to_string(Aircraft::CargoConfig::Algorithm algorithm) {
    switch (algorithm) {
        case Aircraft::CargoConfig::Algorithm::AUTO:
            return "AUTO";
        case Aircraft::CargoConfig::Algorithm::L:
            return "L";
        case Aircraft::CargoConfig::Algorithm::H:
            return "H";
        default:
            return "UNKNOWN";
    }
}

const string Aircraft::CargoConfig::repr(const CargoConfig& config) {
    return "<CargoConfig " + to_string(config.l) + "|" + to_string(config.h) + ">";
}


#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict to_dict(const Aircraft& ac) {
    py::gil_scoped_acquire acquire;
    py::function round = py::module::import("builtins").attr("round");
    py::dict d(
        "id"_a=ac.id,
        "shortname"_a=ac.shortname,
        "manufacturer"_a=ac.manufacturer,
        "name"_a=ac.name,
        "type"_a=to_string(ac.type),
        "priority"_a=ac.priority,
        "eid"_a=ac.eid,
        "ename"_a=ac.ename,
        "speed"_a=round(ac.speed, 3),
        "fuel"_a=round(ac.fuel, 3),
        "co2"_a=round(ac.co2, 3),
        "cost"_a=ac.cost,
        "capacity"_a=ac.capacity,
        "rwy"_a=ac.rwy,
        "check_cost"_a=ac.check_cost,
        "range"_a=ac.range,
        "ceil"_a=ac.ceil,
        "maint"_a=ac.maint,
        "pilots"_a=ac.pilots,
        "crew"_a=ac.crew,
        "engineers"_a=ac.engineers,
        "technicians"_a=ac.technicians,
        "img"_a=ac.img,
        "wingspan"_a=ac.wingspan,
        "length"_a=ac.length,
        "speed_mod"_a=ac.speed_mod,
        "fuel_mod"_a=ac.fuel_mod,
        "co2_mod"_a=ac.co2_mod
    );
    py::gil_scoped_release release;
    return d;
}

py::dict to_dict(const Aircraft::PaxConfig& pc) {
    return py::dict(
        "y"_a=pc.y,
        "j"_a=pc.j,
        "f"_a=pc.f,
        "algorithm"_a=to_string(pc.algorithm)
    );
}

py::dict to_dict(const Aircraft::CargoConfig& cc) {
    return py::dict(
        "l"_a=cc.l,
        "h"_a=cc.h,
        "algorithm"_a=to_string(cc.algorithm)
    );
}

void pybind_init_aircraft(py::module_& m) {
    py::module_ m_ac = m.def_submodule("aircraft");
    
    py::class_<Aircraft, shared_ptr<Aircraft>> ac_class(m_ac, "Aircraft");
    
    py::class_<Aircraft::PaxConfig> pc_class(ac_class, "PaxConfig");
    py::enum_<Aircraft::PaxConfig::Algorithm>(pc_class, "Algorithm")
        .value("AUTO", Aircraft::PaxConfig::Algorithm::AUTO)
        .value("FJY", Aircraft::PaxConfig::Algorithm::FJY).value("FYJ", Aircraft::PaxConfig::Algorithm::FYJ)
        .value("JFY", Aircraft::PaxConfig::Algorithm::JFY).value("JYF", Aircraft::PaxConfig::Algorithm::JYF)
        .value("YJF", Aircraft::PaxConfig::Algorithm::YJF).value("YFJ", Aircraft::PaxConfig::Algorithm::YFJ);
    pc_class
        .def_readonly("y", &Aircraft::PaxConfig::y)
        .def_readonly("j", &Aircraft::PaxConfig::j)
        .def_readonly("f", &Aircraft::PaxConfig::f)
        .def_readonly("valid", &Aircraft::PaxConfig::valid)
        .def_readonly("algorithm", &Aircraft::PaxConfig::algorithm)
        .def("__repr__", &Aircraft::PaxConfig::repr)
        .def("to_dict", py::overload_cast<const Aircraft::PaxConfig&>(&to_dict));

    py::class_<Aircraft::CargoConfig> cc_class(ac_class, "CargoConfig");
    py::enum_<Aircraft::CargoConfig::Algorithm>(cc_class, "Algorithm")
        .value("AUTO", Aircraft::CargoConfig::Algorithm::AUTO)
        .value("L", Aircraft::CargoConfig::Algorithm::L).value("H", Aircraft::CargoConfig::Algorithm::H);
    cc_class
        .def_readonly("l", &Aircraft::CargoConfig::l)
        .def_readonly("h", &Aircraft::CargoConfig::h)
        .def_readonly("valid", &Aircraft::CargoConfig::valid)
        .def_readonly("algorithm", &Aircraft::CargoConfig::algorithm)
        .def("__repr__", &Aircraft::CargoConfig::repr)
        .def("to_dict", py::overload_cast<const Aircraft::CargoConfig&>(&to_dict));

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
        .def_readonly("speed_mod", &Aircraft::speed_mod)
        .def_readonly("fuel_mod", &Aircraft::fuel_mod)
        .def_readonly("co2_mod", &Aircraft::co2_mod)
        .def_readonly("fourx_mod", &Aircraft::fourx_mod)
        .def_readonly("valid", &Aircraft::valid)
        .def("__repr__", &Aircraft::repr)
        .def("to_dict", py::overload_cast<const Aircraft&>(&to_dict));

    py::enum_<Aircraft::SearchType>(ac_class, "SearchType")
        .value("ALL", Aircraft::SearchType::ALL)
        .value("ID", Aircraft::SearchType::ID)
        .value("SHORTNAME", Aircraft::SearchType::SHORTNAME)
        .value("NAME", Aircraft::SearchType::NAME);
    py::class_<Aircraft::ParseResult>(ac_class, "ParseResult")
        .def_readonly("search_type", &Aircraft::ParseResult::search_type)
        .def_readonly("search_str", &Aircraft::ParseResult::search_str)
        .def_readonly("priority", &Aircraft::ParseResult::priority)
        .def_readonly("speed_mod", &Aircraft::ParseResult::speed_mod)
        .def_readonly("fuel_mod", &Aircraft::ParseResult::fuel_mod)
        .def_readonly("co2_mod", &Aircraft::ParseResult::co2_mod);
    py::class_<Aircraft::SearchResult>(ac_class, "SearchResult")
        .def(py::init<shared_ptr<Aircraft>, Aircraft::ParseResult>())
        .def_readonly("ac", &Aircraft::SearchResult::ac)
        .def_readonly("parse_result", &Aircraft::SearchResult::parse_result);
    py::class_<Aircraft::Suggestion>(ac_class, "Suggestion")
        .def(py::init<shared_ptr<Aircraft>, double>())
        .def_readonly("ac", &Aircraft::Suggestion::ac)
        .def_readonly("score", &Aircraft::Suggestion::score);
    ac_class
        .def_static("search", &Aircraft::search, "s"_a, py::arg_v("user", User::Default(), "am4utils._core.game.User.Default()"))
        .def_static("suggest", &Aircraft::suggest, "s"_a);
}
#endif