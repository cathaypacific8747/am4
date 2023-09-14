#include <iostream>
#include "include/game.hpp"
#include "include/db.hpp"

User::User() :
    id("00000000-0000-0000-0000-000000000000"),
    username(""), game_id(0), game_name(""), game_mode(GameMode::EASY),
    discord_id(0),
    wear_training(0), repair_training(0), l_training(0), h_training(0),
    fuel_training(0), co2_training(0),
    fuel_price(700), co2_price(120),
    accumulated_count(0),
    load(0.87),
    income_loss_tol(0.0),
    fourx(false),
    role(User::Role::USER),
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
    income_loss_tol(chunk->GetValue(16, row).GetValue<double>()),
    fourx(chunk->GetValue(17, row).GetValue<bool>()),
    role(static_cast<Role>(chunk->GetValue(18, row).GetValue<uint8_t>())),
    valid(true)
{}

User User::Default(bool realism) {
    User user;
    user.valid = true;
    if (realism) {
        user.id = "00000000-0000-0000-0000-000000000001";
        user.game_mode = GameMode::REALISM;
    }
    return user;
}

inline User to_user(duckdb::unique_ptr<duckdb::QueryResult> result) {
    if (result->HasError()) throw DatabaseException(result->GetError());
    auto chunk = result->Fetch();
    return chunk && chunk->size() != 0 ? User(chunk, 0) : User();
}

User User::create(const string& username, const string& password, uint32_t game_id, const string& game_name, User::GameMode game_mode, uint64_t discord_id) {
    // https://github.com/duckdb/duckdb/issues/1631#issuecomment-821787604
    // UNIQUE and UPDATE don't work well together, manually checking if user exists
    auto result = Database::Client()->verify_user_by_username->Execute(username.c_str());
    CHECK_SUCCESS_REF(result);
    auto chunk = result->Fetch();
    if (chunk && chunk->size() != 0) return User();
    
    // workaround for https://github.com/duckdb/duckdb/issues/8310 & windows linking issues with QueryParamsRecursive
    duckdb::vector<duckdb::Value> values{
        duckdb::Value::CreateValue<string>(username),
        duckdb::Value::CreateValue<string>(password),
        duckdb::Value::CreateValue<uint32_t>(game_id),
        duckdb::Value::CreateValue<string>(game_name),
        duckdb::Value::CreateValue<bool>(static_cast<bool>(game_mode)),
        duckdb::Value::CreateValue<uint64_t>(discord_id)
    };
    return to_user(Database::Client()->insert_user->Execute(values, false));
}

User User::from_id(const string& id) {
    return to_user(Database::Client()->get_user_by_id->Execute(id.c_str()));
}

User User::from_username(const string& username) {
    return to_user(Database::Client()->get_user_by_username->Execute(username.c_str()));
}

User User::from_game_id(uint32_t game_id) {
    return to_user(Database::Client()->get_user_by_game_id->Execute(game_id));
}

User User::from_game_name(const string& game_name) {
    return to_user(Database::Client()->get_user_by_game_name->Execute(game_name.c_str()));
}

User User::from_discord_id(uint64_t discord_id) {
    return to_user(Database::Client()->get_user_by_discord_id->Execute(discord_id));
}

string User::get_password() {
    if (!this->valid) return "";
    auto result = Database::Client()->get_user_password->Execute(this->id.c_str());
    CHECK_SUCCESS_REF(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return "";
    return chunk->GetValue(0, 0).GetValue<string>();
}

bool User::set_username(const string& new_uname) {
    auto result = Database::Client()->verify_user_by_username->Execute(new_uname.c_str());
    CHECK_SUCCESS_REF(result);
    auto chunk = result->Fetch();
    if (chunk && chunk->size() != 0) return false;

    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_username->Execute(new_uname.c_str(), this->id.c_str()));
    this->username = new_uname;
    return true;
}

bool User::set_password(const string& new_pw) {
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_password->Execute(new_pw.c_str(), this->id.c_str()));
    return true;
}

bool User::set_game_id(uint32_t new_gid) {
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_game_id->Execute(new_gid, this->id.c_str()));
    this->game_id = new_gid;
    return true;
}

bool User::set_game_name(const string& new_gn) {
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_game_name->Execute(new_gn.c_str(), this->id.c_str()));
    this->game_name = new_gn;
    return true;
}

bool User::set_game_mode(User::GameMode new_gm) {
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_game_mode->Execute(static_cast<bool>(new_gm), this->id.c_str()));
    this->game_mode = new_gm;
    return true;
}

bool User::set_discord_id(uint64_t new_did) {
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_discord_id->Execute(new_did, this->id.c_str()));
    this->discord_id = new_did;
    return true;
}

bool User::set_wear_training(uint8_t new_wt) {
    if (new_wt > 5) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_wear_training->Execute(new_wt, this->id.c_str()));
    this->wear_training = new_wt;
    return true;
}

bool User::set_repair_training(uint8_t new_rt) {
    if (new_rt > 5) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_repair_training->Execute(new_rt, this->id.c_str()));
    this->repair_training = new_rt;
    return true;
}

bool User::set_l_training(uint8_t new_lt) {
    if (new_lt > 6) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_l_training->Execute(new_lt, this->id.c_str()));
    this->l_training = new_lt;
    return true;
}

bool User::set_h_training(uint8_t new_ht) {
    if (new_ht > 6) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_h_training->Execute(new_ht, this->id.c_str()));
    this->h_training = new_ht;
    return true;
}

bool User::set_fuel_training(uint8_t new_ft) {
    if (new_ft > 3) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_fuel_training->Execute(new_ft, this->id.c_str()));
    this->fuel_training = new_ft;
    return true;
}

bool User::set_co2_training(uint8_t new_ct) {
    if (new_ct > 5) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_co2_training->Execute(new_ct, this->id.c_str()));
    this->co2_training = new_ct;
    return true;
}

bool User::set_fuel_price(uint16_t new_fp) {
    if (new_fp > 3000) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_fuel_price->Execute(new_fp, this->id.c_str()));
    this->fuel_price = new_fp;
    return true;
}

bool User::set_co2_price(uint8_t new_cp) {
    if (new_cp > 200) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_co2_price->Execute(new_cp, this->id.c_str()));
    this->co2_price = new_cp;
    return true;
}

bool User::set_accumulated_count(uint16_t new_acc) {
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_accumulated_count->Execute(new_acc, this->id.c_str()));
    this->accumulated_count = new_acc;
    return true;
}

bool User::set_load(double new_l) {
    if (new_l <= 0 || new_l > 1) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_load->Execute(new_l, this->id.c_str()));
    this->load = new_l;
    return true;
}

bool User::set_income_tolerance(double new_ilt) {
    if (new_ilt < 0 || new_ilt > 1) return false;
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_income_loss_tol->Execute(new_ilt, this->id.c_str()));
    this->income_loss_tol = new_ilt;
    return true;
}

bool User::set_fourx(bool new_fx) {
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_fourx->Execute(new_fx, this->id.c_str()));
    this->fourx = new_fx;
    return true;
}

bool User::set_role(const User::Role& new_role) {
    VERIFY_UPDATE_SUCCESS(Database::Client()->update_user_role->Execute(static_cast<uint8_t>(new_role), this->id.c_str()));
    this->role = new_role;
    return true;
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

inline const string to_string(User::Role role) {
    switch (role) {
        case User::Role::USER:
            return "USER";
        case User::Role::TRUSTED_USER:
            return "TRUSTED_USER";
        case User::Role::ADMIN:
            return "ADMIN";
        default:
            return "[UNKNOWN]";
    }
}

const string User::repr(const User& user) {
    if (!user.valid) return "<User.INVALID>";
    return "<User id=" + user.id + " username=" + user.username + " discord_id=" + to_string(user.discord_id) + " game_id=" + to_string(user.game_id) + " game_name=" + user.game_name + " game_mode=" + to_string(user.game_mode) + ">";
}

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

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict to_dict(const User& user) {
    return py::dict(
        "id"_a = user.id,
        "username"_a = user.username,
        "discord_id"_a = user.discord_id,
        "game_id"_a = user.game_id,
        "game_name"_a = user.game_name,
        "game_mode"_a = to_string(user.game_mode),
        "wear_training"_a = user.wear_training,
        "repair_training"_a = user.repair_training,
        "l_training"_a = user.l_training,
        "h_training"_a = user.h_training,
        "fuel_training"_a = user.fuel_training,
        "co2_training"_a = user.co2_training,
        "fuel_price"_a = user.fuel_price,
        "co2_price"_a = user.co2_price,
        "accumulated_count"_a = user.accumulated_count,
        "load"_a = user.load,
        "income_loss_tol"_a = user.income_loss_tol,
        "fourx"_a = user.fourx,
        "role"_a = to_string(user.role)
    );
}

void pybind_init_game(py::module_& m) {
    py::module_ m_game = m.def_submodule("game");

    py::class_<User> user_class(m_game, "User");
    py::enum_<User::GameMode>(user_class, "GameMode")
        .value("EASY", User::GameMode::EASY)
        .value("REALISM", User::GameMode::REALISM);
    py::enum_<User::Role>(user_class, "Role")
        .value("USER", User::Role::USER)
        .value("TRUSTED_USER", User::Role::TRUSTED_USER)
        .value("ADMIN", User::Role::ADMIN);
    user_class
        .def_readonly("id", &User::id)
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
        .def_static("create", &User::create, "username"_a, "password"_a, "game_id"_a, "game_name"_a, "game_mode"_a = User::GameMode::EASY, "discord_id"_a = 0)
        .def_static("from_id", &User::from_id, "id"_a)
        .def_static("from_username", &User::from_username, "username"_a)
        .def_static("from_game_id", &User::from_game_id, "game_id"_a)
        .def_static("from_game_name", &User::from_game_name, "game_name"_a)
        .def_static("from_discord_id", &User::from_discord_id, "discord_id"_a)
        .def("get_password", &User::get_password)
        .def("set_username", &User::set_username, "username"_a)
        .def("set_password", &User::set_password, "password"_a)
        .def("set_game_id", &User::set_game_id, "game_id"_a)
        .def("set_game_name", &User::set_game_name, "game_name"_a)
        .def("set_game_mode", &User::set_game_mode, "game_mode"_a)
        .def("set_discord_id", &User::set_discord_id, "discord_id"_a)
        .def("set_wear_training", &User::set_wear_training, "wear_training"_a)
        .def("set_repair_training", &User::set_repair_training, "repair_training"_a)
        .def("set_l_training", &User::set_l_training, "l_training"_a)
        .def("set_h_training", &User::set_h_training, "h_training"_a)
        .def("set_fuel_training", &User::set_fuel_training, "fuel_training"_a)
        .def("set_co2_training", &User::set_co2_training, "co2_training"_a)
        .def("set_fuel_price", &User::set_fuel_price, "fuel_price"_a)
        .def("set_co2_price", &User::set_co2_price, "co2_price"_a)
        .def("set_accumulated_count", &User::set_accumulated_count, "accumulated_count"_a)
        .def("set_load", &User::set_load, "load"_a)
        .def("set_income_tolerance", &User::set_income_tolerance, "income_loss_tol"_a)
        .def("set_fourx", &User::set_fourx, "fourx"_a)
        .def("set_role", &User::set_role, "role"_a)
        .def("to_dict", py::overload_cast<const User&>(&to_dict))
        .def("__repr__", &User::repr);

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

}
#endif