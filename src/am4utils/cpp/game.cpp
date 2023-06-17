#include "include/game.hpp"

User::User() :
    id(0), game_id(0),
    game_mode(GameMode::EASY),
    l_training(0), h_training(0),
    fuel_price(700), co2_price(120),
    fuel_training(0), co2_training(0),
    override_load(false), load(85)
{};

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

Campaign::Campaign() :
    pax_activated(Airline::NONE),
    cargo_activated(Airline::NONE),
    eco_activated(Eco::NONE)
{};

Campaign::Campaign(Airline pax_activated, Airline cargo_activated, Eco eco_activated) :
    pax_activated(pax_activated),
    cargo_activated(cargo_activated),
    eco_activated(eco_activated)
{};

Campaign Campaign::Default() {
    return Campaign(Airline::C4_24HR, Airline::C4_24HR, Eco::C_24HR);
}

const double Campaign::estimate_pax_reputation(double base_reputation) {
    double reputation = base_reputation;
    reputation += Campaign::_estimate_airline_reputation(pax_activated);
    reputation += Campaign::_estimate_eco_reputation(eco_activated);
    return reputation;
}

const double Campaign::estimate_cargo_reputation(double base_reputation) {
    double reputation = base_reputation;
    reputation += Campaign::_estimate_airline_reputation(cargo_activated);
    reputation += Campaign::_estimate_eco_reputation(eco_activated);
    return reputation;
}

const double Campaign::_estimate_airline_reputation(Airline airline) {
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

const double Campaign::_estimate_eco_reputation(Eco eco) {
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