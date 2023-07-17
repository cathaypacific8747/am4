#include "include/game.hpp"

Campaign::Campaign() :
    pax_activated(Airline::NONE),
    cargo_activated(Airline::NONE),
    eco_activated(Eco::NONE)
{}

Campaign::Campaign(Airline pax_activated, Airline cargo_activated, Eco eco_activated) :
    pax_activated(pax_activated),
    cargo_activated(cargo_activated),
    eco_activated(eco_activated)
{}

Campaign Campaign::Default() {
    return Campaign(Airline::C4_24HR, Airline::C4_24HR, Eco::C_24HR);
}

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
        case Airline::C4_4HR: case Airline::C4_8HR: case Airline::C4_12HR: case Airline::C4_16HR: case Airline::C4_20HR: case Airline::C4_24HR:
            return 30;
        case Airline::C3_4HR: case Airline::C3_8HR: case Airline::C3_12HR: case Airline::C3_16HR: case Airline::C3_20HR: case Airline::C3_24HR:
            return 21.5;
        case Airline::C2_4HR: case Airline::C2_8HR: case Airline::C2_12HR: case Airline::C2_16HR: case Airline::C2_20HR: case Airline::C2_24HR:
            return 14;
        case Airline::C1_4HR: case Airline::C1_8HR: case Airline::C1_12HR: case Airline::C1_16HR: case Airline::C1_20HR: case Airline::C1_24HR:
            return 7.5;
        case Airline::NONE:
            return 0;
    }
    return 0;
}

double Campaign::_estimate_eco_reputation(Eco eco) {
    switch (eco) {
        case Eco::C_4HR: case Eco::C_8HR: case Eco::C_12HR: case Eco::C_16HR: case Eco::C_20HR: case Eco::C_24HR:
            return 10;
        case Eco::NONE:
            return 0;
    }
    return 0;
}

bool Campaign::_set(const string& s) {
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

Campaign Campaign::parse(const string& s) {
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

User::User() :
    id(0), game_id(0),
    game_mode(GameMode::EASY),
    l_training(0), h_training(0),
    fuel_price(700), co2_price(120),
    fuel_training(0), co2_training(0),
    load(87)
{}

const string to_string(User::GameMode game_mode) {
    switch (game_mode) {
        case User::GameMode::EASY:
            return "EASY";
        case User::GameMode::REALISM:
            return "HARD";
        default:
            return "[UNKNOWN]";
    }
}

const string User::repr(const User& user) {
    return "<User " + to_string(user.game_mode) + " id=" + to_string(user.id) + " game_id=" + to_string(user.game_id) + ">";
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

void pybind_init_game(py::module_& m) {
    py::module_ m_game = m.def_submodule("game");

    py::class_<Campaign> campaign_class(m_game, "Campaign");
    py::enum_<Campaign::Airline>(campaign_class, "Airline")
        .value("C4_4HR", Campaign::Airline::C4_4HR).value("C4_8HR", Campaign::Airline::C4_8HR).value("C4_12HR", Campaign::Airline::C4_12HR).value("C4_16HR", Campaign::Airline::C4_16HR).value("C4_20HR", Campaign::Airline::C4_20HR).value("C4_24HR", Campaign::Airline::C4_24HR)
        .value("C3_4HR", Campaign::Airline::C3_4HR).value("C3_8HR", Campaign::Airline::C3_8HR).value("C3_12HR", Campaign::Airline::C3_12HR).value("C3_16HR", Campaign::Airline::C3_16HR).value("C3_20HR", Campaign::Airline::C3_20HR).value("C3_24HR", Campaign::Airline::C3_24HR)
        .value("C2_4HR", Campaign::Airline::C2_4HR).value("C2_8HR", Campaign::Airline::C2_8HR).value("C2_12HR", Campaign::Airline::C2_12HR).value("C2_16HR", Campaign::Airline::C2_16HR).value("C2_20HR", Campaign::Airline::C2_20HR).value("C2_24HR", Campaign::Airline::C2_24HR)
        .value("C1_4HR", Campaign::Airline::C1_4HR).value("C1_8HR", Campaign::Airline::C1_8HR).value("C1_12HR", Campaign::Airline::C1_12HR).value("C1_16HR", Campaign::Airline::C1_16HR).value("C1_20HR", Campaign::Airline::C1_20HR).value("C1_24HR", Campaign::Airline::C1_24HR)
        .value("NONE", Campaign::Airline::NONE);
    py::enum_<Campaign::Eco>(campaign_class, "Eco")
        .value("C_4HR", Campaign::Eco::C_4HR).value("C_8HR", Campaign::Eco::C_8HR).value("C_12HR", Campaign::Eco::C_12HR).value("C_16HR", Campaign::Eco::C_16HR).value("C_20HR", Campaign::Eco::C_20HR).value("C_24HR", Campaign::Eco::C_24HR)
        .value("NONE", Campaign::Eco::NONE);
    campaign_class
        .def_readonly("pax_activated", &Campaign::pax_activated)
        .def_readonly("cargo_activated", &Campaign::cargo_activated)
        .def_readonly("eco_activated", &Campaign::eco_activated)
        .def_static("Default", &Campaign::Default)
        .def_static("parse", &Campaign::parse, "s"_a)
        .def("estimate_pax_reputation", &Campaign::estimate_pax_reputation, "base_reputation"_a = 45)
        .def("estimate_cargo_reputation", &Campaign::estimate_cargo_reputation, "base_reputation"_a = 45);

    py::class_<User> user_class(m_game, "User");
    py::enum_<User::GameMode>(user_class, "GameMode")
        .value("EASY", User::GameMode::EASY)
        .value("REALISM", User::GameMode::REALISM);
    user_class
        .def(py::init<>())
        .def_readonly("id", &User::id)
        .def_readonly("game_id", &User::game_id)
        .def_readonly("ign", &User::ign)
        .def_readonly("game_mode", &User::game_mode)
        .def_readonly("l_training", &User::l_training)
        .def_readonly("h_training", &User::h_training)
        .def_readonly("fuel_price", &User::fuel_price)
        .def_readonly("co2_price", &User::co2_price)
        .def_readonly("fuel_training", &User::fuel_training)
        .def_readonly("co2_training", &User::co2_training)
        .def_readonly("load", &User::load)
        .def("__repr__", &User::repr);
}
#endif