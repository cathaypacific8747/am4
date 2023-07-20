#include <iostream>
#include "include/game.hpp"
#include "include/db.hpp"

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
    id("00000000-0000-0000-0000-000000000000"),
    username(""), game_id(0), game_name(""), game_mode(GameMode::EASY),
    discord_id(0),
    wear_training(0), repair_training(0),
    l_training(0), h_training(0),
    fuel_training(0), co2_training(0),
    fuel_price(700), co2_price(120),
    accumulated_count(0),
    load(87),
    role("user"),
    valid(false)
{}

User::User(const duckdb::unique_ptr<duckdb::DataChunk>& chunk, idx_t row) :
    id(chunk->GetValue(0, row).GetValue<string>()),
    username(chunk->GetValue(1, row).GetValue<string>()),
    game_id(chunk->GetValue(2, row).GetValue<uint32_t>()),
    game_name(chunk->GetValue(3, row).GetValue<string>()),
    game_mode(static_cast<GameMode>(chunk->GetValue(4, row).GetValue<bool>())),
    discord_id(chunk->GetValue(5, row).GetValue<uint64_t>()),
    wear_training(chunk->GetValue(6, row).GetValue<uint8_t>()),
    repair_training(chunk->GetValue(7, row).GetValue<uint8_t>()),
    l_training(chunk->GetValue(8, row).GetValue<uint8_t>()),
    h_training(chunk->GetValue(9, row).GetValue<uint8_t>()),
    fuel_training(chunk->GetValue(10, row).GetValue<uint8_t>()),
    co2_training(chunk->GetValue(11, row).GetValue<uint8_t>()),
    fuel_price(chunk->GetValue(12, row).GetValue<uint16_t>()),
    co2_price(chunk->GetValue(13, row).GetValue<uint8_t>()),
    accumulated_count(chunk->GetValue(14, row).GetValue<uint16_t>()),
    load(chunk->GetValue(15, row).GetValue<double>()),
    role(chunk->GetValue(16, row).GetValue<string>()),
    valid(true)
{}

User User::Default(bool realism) {
    User user;
    user.role = "user";
    user.valid = true;
    if (realism) {
        user.id = "00000000-0000-0000-0000-000000000001";
        user.game_mode = GameMode::REALISM;
    }
    return user;
}

inline User to_user(duckdb::unique_ptr<QueryResult> result) {
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    return chunk && chunk->size() != 0 ? User(chunk, 0) : User();
}

User User::create(const string& username, const string& password, uint32_t game_id, const string& game_name, User::GameMode game_mode, uint64_t discord_id) {
    // https://github.com/duckdb/duckdb/issues/8310
    // return to_user(Database::Client()->insert_user->Execute(username.c_str(), password.c_str(), game_id, game_name.c_str(), static_cast<bool>(game_mode), discord_id));
    return to_user(Database::Client()->connection->Query(INSERT_USER_STATEMENT, username.c_str(), password.c_str(), game_id, game_name.c_str(), static_cast<bool>(game_mode), discord_id));
}

User User::from_id(const string& id) {
    return to_user(Database::Client()->get_user_by_id->Execute(id.c_str()));
}

User User::from_username(const string& username) {
    return to_user(Database::Client()->get_user_by_username->Execute(username.c_str()));
}

User User::from_discord_id(uint64_t discord_id) {
    return to_user(Database::Client()->get_user_by_discord_id->Execute(discord_id));
}

User User::from_game_id(uint32_t game_id) {
    return to_user(Database::Client()->get_user_by_game_id->Execute(game_id));
}

User User::from_game_name(const string& game_name) {
    return to_user(Database::Client()->get_user_by_ign->Execute(game_name.c_str()));
}

// #include <iostream>
void User::set_game_mode(User::GameMode game_mode) {
    auto result = Database::Client()->update_user_game_mode->Execute(static_cast<bool>(game_mode), id.c_str());
    VERIFY_SUCCESS_AND_SIZE(result, 1);
    this->game_mode = game_mode;
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

const string User::repr(const User& user) {
    if (!user.valid) return "<User.INVALID>";
    return "<User id=" + user.id + " username=" + user.username + " discord_id=" + to_string(user.discord_id) + " game_id=" + to_string(user.game_id) + " game_name=" + user.game_name + " game_mode=" + to_string(user.game_mode) + ">";
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
        .def_readonly("id", &User::id)
        .def_readonly("username", &User::username)
        .def_readonly("discord_id", &User::discord_id)
        .def_readonly("game_id", &User::game_id)
        .def_readonly("game_name", &User::game_name)
        .def_readonly("game_mode", &User::game_mode)
        .def_readonly("wear_training", &User::wear_training)
        .def_readonly("repair_training", &User::repair_training)
        .def_readonly("l_training", &User::l_training)
        .def_readonly("h_training", &User::h_training)
        .def_readonly("fuel_training", &User::fuel_training)
        .def_readonly("co2_training", &User::co2_training)
        .def_readonly("fuel_price", &User::fuel_price)
        .def_readonly("co2_price", &User::co2_price)
        .def_readonly("accumulated_count", &User::accumulated_count)
        .def_readonly("load", &User::load)
        .def_readonly("valid", &User::valid)
        .def_readonly("role", &User::role)
        .def_static("Default", &User::Default, "realism"_a = false)
        .def_static("create", &User::create, "username"_a, "password"_a, "game_id"_a, "game_name"_a, "game_mode"_a = User::GameMode::EASY, "discord_id"_a = 0)
        .def_static("from_id", &User::from_id, "id"_a)
        .def_static("from_username", &User::from_username, "username"_a)
        .def_static("from_discord_id", &User::from_discord_id, "discord_id"_a)
        .def_static("from_game_id", &User::from_game_id, "game_id"_a)
        .def_static("from_game_name", &User::from_game_name, "game_name"_a)
        .def("__repr__", &User::repr);
}
#endif