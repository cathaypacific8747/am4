#include "include/game.hpp"

#include <iostream>

#include "include/db.hpp"

User::User()
    : id("00000000-0000-0000-0000-000000000000"),
      username(""),
      game_id(0),
      game_name(""),
      game_mode(GameMode::EASY),
      discord_id(0),
      wear_training(0),
      repair_training(0),
      l_training(0),
      h_training(0),
      fuel_training(0),
      co2_training(0),
      fuel_price(700),
      co2_price(120),
      accumulated_count(0),
      load(0.87),
      income_loss_tol(0.1),
      fourx(false),
      role(User::Role::USER),
      valid(false) {}

User User::Default(bool realism) {
    User user;
    user.valid = true;
    if (realism) {
        user.id = "00000000-0000-0000-0000-000000000001";
        user.game_mode = GameMode::REALISM;
    }
    return user;
}

inline const string to_string(User::GameMode game_mode) {
    switch (game_mode) {
        case User::GameMode::EASY:
            return "EASY";
        case User::GameMode::REALISM:
            return "REALISM";
        default:
            return "[UNKNOWN]";
    }
}

inline User::GameMode gamemode_from_string(const string &s) {
    if (s == "REALISM") return User::GameMode::REALISM;
    return User::GameMode::EASY;
}

inline const string to_string(User::Role role) {
    switch (role) {
        case User::Role::USER:
            return "USER";
        case User::Role::TRUSTED_USER:
            return "TRUSTED_USER";
        case User::Role::TRUSTED_USER_2:
            return "TRUSTED_USER_2";
        case User::Role::TOP_ALLIANCE_MEMBER:
            return "TOP_ALLIANCE_MEMBER";
        case User::Role::TOP_ALLIANCE_ADMIN:
            return "TOP_ALLIANCE_ADMIN";
        case User::Role::HELPER:
            return "HELPER";
        case User::Role::MODERATOR:
            return "MODERATOR";
        case User::Role::ADMIN:
            return "ADMIN";
        case User::Role::GLOBAL_ADMIN:
            return "GLOBAL_ADMIN";
        default:
            return "[UNKNOWN]";
    }
}

inline User::Role role_from_string(const string &s) {
    if (s == "USER") return User::Role::USER;
    if (s == "TRUSTED_USER") return User::Role::TRUSTED_USER;
    if (s == "TRUSTED_USER_2") return User::Role::TRUSTED_USER_2;
    if (s == "TOP_ALLIANCE_MEMBER") return User::Role::TOP_ALLIANCE_MEMBER;
    if (s == "TOP_ALLIANCE_ADMIN") return User::Role::TOP_ALLIANCE_ADMIN;
    if (s == "HELPER") return User::Role::HELPER;
    if (s == "MODERATOR") return User::Role::MODERATOR;
    if (s == "ADMIN") return User::Role::ADMIN;
    if (s == "GLOBAL_ADMIN") return User::Role::GLOBAL_ADMIN;
    return User::Role::USER;
}

const string User::repr(const User &user) {
    if (!user.valid) return "<User.INVALID>";
    return "<User id=" + user.id + " username=" + user.username + " discord_id=" + to_string(user.discord_id) +
           " game_id=" + to_string(user.game_id) + " game_name=" + user.game_name +
           " game_mode=" + to_string(user.game_mode) + ">";
}

Campaign::Campaign() : pax_activated(Airline::NONE), cargo_activated(Airline::NONE), eco_activated(Eco::NONE) {}

Campaign::Campaign(Airline pax_activated, Airline cargo_activated, Eco eco_activated)
    : pax_activated(pax_activated), cargo_activated(cargo_activated), eco_activated(eco_activated) {}

Campaign Campaign::Default() { return Campaign(Airline::C4_24HR, Airline::C4_24HR, Eco::C_24HR); }

double Campaign::estimate_pax_reputation(double base_reputation) {
    double reputation = base_reputation;
    reputation += Campaign::_estimate_airline_reputation(pax_activated);
    reputation += Campaign::_estimate_eco_reputation(eco_activated);
    return reputation;
}

double Campaign::estimate_cargo_reputation(double base_reputation) {
    double reputation = base_reputation;
    reputation += Campaign::_estimate_airline_reputation(cargo_activated);
    reputation += Campaign::_estimate_eco_reputation(eco_activated);
    return reputation;
}

double Campaign::_estimate_airline_reputation(Airline airline) {
    switch (airline) {
        case Airline::C4_4HR:
        case Airline::C4_8HR:
        case Airline::C4_12HR:
        case Airline::C4_16HR:
        case Airline::C4_20HR:
        case Airline::C4_24HR:
            return 30;
        case Airline::C3_4HR:
        case Airline::C3_8HR:
        case Airline::C3_12HR:
        case Airline::C3_16HR:
        case Airline::C3_20HR:
        case Airline::C3_24HR:
            return 21.5;
        case Airline::C2_4HR:
        case Airline::C2_8HR:
        case Airline::C2_12HR:
        case Airline::C2_16HR:
        case Airline::C2_20HR:
        case Airline::C2_24HR:
            return 14;
        case Airline::C1_4HR:
        case Airline::C1_8HR:
        case Airline::C1_12HR:
        case Airline::C1_16HR:
        case Airline::C1_20HR:
        case Airline::C1_24HR:
            return 7.5;
        case Airline::NONE:
            return 0;
    }
    return 0;
}

double Campaign::_estimate_eco_reputation(Eco eco) {
    switch (eco) {
        case Eco::C_4HR:
        case Eco::C_8HR:
        case Eco::C_12HR:
        case Eco::C_16HR:
        case Eco::C_20HR:
        case Eco::C_24HR:
            return 10;
        case Eco::NONE:
            return 0;
    }
    return 0;
}

bool Campaign::_set(const string &s) {
    if (s == "C1") {
        pax_activated = Airline::C1_24HR;
        cargo_activated = Airline::C1_24HR;
        return true;
    } else if (s == "C2") {
        pax_activated = Airline::C2_24HR;
        cargo_activated = Airline::C2_24HR;
        return true;
    } else if (s == "C3") {
        pax_activated = Airline::C3_24HR;
        cargo_activated = Airline::C3_24HR;
        return true;
    } else if (s == "C4") {
        pax_activated = Airline::C4_24HR;
        cargo_activated = Airline::C4_24HR;
        return true;
    } else if (s == "E") {
        eco_activated = Eco::C_24HR;
        return true;
    }
    return false;
}

Campaign Campaign::parse(const string &s) {
    Campaign campaign;
    string s_upper = s;
    s_upper.erase(std::remove_if(s_upper.begin(), s_upper.end(), isspace), s_upper.end());
    if (s_upper.empty()) return campaign;

    std::transform(s_upper.begin(), s_upper.end(), s_upper.begin(), ::toupper);
    size_t pos = s_upper.find(',');
    if (pos == string::npos) {
        campaign._set(s_upper);
    } else {
        campaign._set(s_upper.substr(0, pos));
        campaign._set(s_upper.substr(pos + 1));
    }
    // TODO: throw exception if not valid
    return campaign;
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict to_dict(const User &user) {
    return py::dict(
        "id"_a = user.id, "username"_a = user.username, "discord_id"_a = user.discord_id, "game_id"_a = user.game_id,
        "game_name"_a = user.game_name, "game_mode"_a = to_string(user.game_mode),
        "wear_training"_a = user.wear_training, "repair_training"_a = user.repair_training,
        "l_training"_a = user.l_training, "h_training"_a = user.h_training, "fuel_training"_a = user.fuel_training,
        "co2_training"_a = user.co2_training, "fuel_price"_a = user.fuel_price, "co2_price"_a = user.co2_price,
        "accumulated_count"_a = user.accumulated_count, "load"_a = user.load,
        "income_loss_tol"_a = user.income_loss_tol, "fourx"_a = user.fourx, "role"_a = to_string(user.role)
    );
}

User from_dict(py::dict &d) {
    User user = User::Default();
    auto p = d.attr("pop");
    user.id = p("id").cast<string>();
    user.username = p("username").cast<string>();
    user.game_id = p("game_id").cast<uint32_t>();
    user.game_name = p("game_name").cast<string>();
    user.game_mode = gamemode_from_string(p("game_mode").cast<std::string>());
    user.discord_id = p("discord_id").cast<uint64_t>();
    user.wear_training = p("wear_training").cast<uint8_t>();
    user.repair_training = p("repair_training").cast<uint8_t>();
    user.l_training = p("l_training").cast<uint8_t>();
    user.h_training = p("h_training").cast<uint8_t>();
    user.fuel_training = p("fuel_training").cast<uint8_t>();
    user.co2_training = p("co2_training").cast<uint8_t>();
    user.fuel_price = p("fuel_price").cast<uint16_t>();
    user.co2_price = p("co2_price").cast<uint8_t>();
    user.accumulated_count = p("accumulated_count").cast<uint16_t>();
    user.load = p("load").cast<double>();
    user.income_loss_tol = p("income_loss_tol").cast<double>();
    user.fourx = p("fourx").cast<bool>();
    user.role = role_from_string(p("role").cast<std::string>());
    user.valid = true;
    return user;
}

void pybind_init_game(py::module_ &m) {
    py::module_ m_game = m.def_submodule("game");

    py::class_<User> user_class(m_game, "User");
    py::enum_<User::GameMode>(user_class, "GameMode")
        .value("EASY", User::GameMode::EASY)
        .value("REALISM", User::GameMode::REALISM);
    py::enum_<User::Role>(user_class, "Role")
        .value("USER", User::Role::USER)
        .value("TRUSTED_USER", User::Role::TRUSTED_USER)
        .value("ADMIN", User::Role::ADMIN);
    user_class.def_readonly("id", &User::id)
        .def_readwrite("username", &User::username)
        .def_readwrite("discord_id", &User::discord_id)
        .def_readwrite("game_id", &User::game_id)
        .def_readwrite("game_name", &User::game_name)
        .def_readwrite("game_mode", &User::game_mode)
        .def_readwrite("wear_training", &User::wear_training)
        .def_readwrite("repair_training", &User::repair_training)
        .def_readwrite("l_training", &User::l_training)
        .def_readwrite("h_training", &User::h_training)
        .def_readwrite("fuel_training", &User::fuel_training)
        .def_readwrite("co2_training", &User::co2_training)
        .def_readwrite("fuel_price", &User::fuel_price)
        .def_readwrite("co2_price", &User::co2_price)
        .def_readwrite("accumulated_count", &User::accumulated_count)
        .def_readwrite("load", &User::load)
        .def_readwrite("income_loss_tol", &User::income_loss_tol)
        .def_readwrite("valid", &User::valid)
        .def_readwrite("fourx", &User::fourx)
        .def_readwrite("role", &User::role)
        .def_static("Default", &User::Default, "realism"_a = false)
        .def_static("from_dict", &from_dict)
        .def(
            "to_dict", py::overload_cast<const User &>(&to_dict),
            "WARNING: dict is passed by reference - will remove added keys!"
        )
        .def("__repr__", &User::repr);

    py::class_<Campaign> campaign_class(m_game, "Campaign");
    py::enum_<Campaign::Airline>(campaign_class, "Airline")
        .value("C4_4HR", Campaign::Airline::C4_4HR)
        .value("C4_8HR", Campaign::Airline::C4_8HR)
        .value("C4_12HR", Campaign::Airline::C4_12HR)
        .value("C4_16HR", Campaign::Airline::C4_16HR)
        .value("C4_20HR", Campaign::Airline::C4_20HR)
        .value("C4_24HR", Campaign::Airline::C4_24HR)
        .value("C3_4HR", Campaign::Airline::C3_4HR)
        .value("C3_8HR", Campaign::Airline::C3_8HR)
        .value("C3_12HR", Campaign::Airline::C3_12HR)
        .value("C3_16HR", Campaign::Airline::C3_16HR)
        .value("C3_20HR", Campaign::Airline::C3_20HR)
        .value("C3_24HR", Campaign::Airline::C3_24HR)
        .value("C2_4HR", Campaign::Airline::C2_4HR)
        .value("C2_8HR", Campaign::Airline::C2_8HR)
        .value("C2_12HR", Campaign::Airline::C2_12HR)
        .value("C2_16HR", Campaign::Airline::C2_16HR)
        .value("C2_20HR", Campaign::Airline::C2_20HR)
        .value("C2_24HR", Campaign::Airline::C2_24HR)
        .value("C1_4HR", Campaign::Airline::C1_4HR)
        .value("C1_8HR", Campaign::Airline::C1_8HR)
        .value("C1_12HR", Campaign::Airline::C1_12HR)
        .value("C1_16HR", Campaign::Airline::C1_16HR)
        .value("C1_20HR", Campaign::Airline::C1_20HR)
        .value("C1_24HR", Campaign::Airline::C1_24HR)
        .value("NONE", Campaign::Airline::NONE);
    py::enum_<Campaign::Eco>(campaign_class, "Eco")
        .value("C_4HR", Campaign::Eco::C_4HR)
        .value("C_8HR", Campaign::Eco::C_8HR)
        .value("C_12HR", Campaign::Eco::C_12HR)
        .value("C_16HR", Campaign::Eco::C_16HR)
        .value("C_20HR", Campaign::Eco::C_20HR)
        .value("C_24HR", Campaign::Eco::C_24HR)
        .value("NONE", Campaign::Eco::NONE);
    campaign_class.def_readonly("pax_activated", &Campaign::pax_activated)
        .def_readonly("cargo_activated", &Campaign::cargo_activated)
        .def_readonly("eco_activated", &Campaign::eco_activated)
        .def_static("Default", &Campaign::Default)
        .def_static("parse", &Campaign::parse, "s"_a)
        .def("estimate_pax_reputation", &Campaign::estimate_pax_reputation, "base_reputation"_a = 45)
        .def("estimate_cargo_reputation", &Campaign::estimate_cargo_reputation, "base_reputation"_a = 45);
}
#endif