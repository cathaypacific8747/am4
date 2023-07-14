#pragma once
#include <string>
#include <algorithm>

using std::string;
using std::to_string;

struct Campaign {
    // type | duration
    enum class Airline : uint8_t {
        C4_4HR = 41, C4_8HR = 42, C4_12HR = 43, C4_16HR = 44, C4_20HR = 45, C4_24HR = 46, // 25-35%
        C3_4HR = 31, C3_8HR = 32, C3_12HR = 33, C3_16HR = 34, C3_20HR = 35, C3_24HR = 36, // 18-25%
        C2_4HR = 21, C2_8HR = 22, C2_12HR = 23, C2_16HR = 24, C2_20HR = 25, C2_24HR = 26, // 10-18%
        C1_4HR = 11, C1_8HR = 12, C1_12HR = 13, C1_16HR = 14, C1_20HR = 15, C1_24HR = 16, // 5-10%
        NONE = 0,
    };

    enum class Eco : uint8_t {
        C_4HR = 51, C_8HR = 52, C_12HR = 53, C_16HR = 54, C_20HR = 55, C_24HR = 56, // 10%
        NONE = 0,
    };

    Airline pax_activated;
    Airline cargo_activated;
    Eco eco_activated;

    Campaign();
    Campaign(Airline pax_activated, Airline cargo_activated, Eco eco_activated);
    static Campaign Default();
    static Campaign parse(const string& s);
    double estimate_pax_reputation(double base_reputation = 45);
    double estimate_cargo_reputation(double base_reputation = 45); // todo: get estimation range

    static double _estimate_airline_reputation(Airline airline);
    static double _estimate_eco_reputation(Eco eco);
    bool _set(const string& s);
};

struct User {
    enum class GameMode {
        EASY = 0,
        REALISM = 1,
    };

    uint64_t id;
    uint32_t game_id;
    string ign;
    GameMode game_mode;
    uint8_t l_training; // 0-6
    uint8_t h_training; // 0-6
    uint16_t fuel_price; // 0-3000
    uint8_t co2_price; // 0-200
    uint8_t fuel_training; // 0-3
    uint8_t co2_training; // 0-5
    
    double load; // 0-100

    User();
    static const string repr(const User& r);
};

const string to_string(User::GameMode game_mode);

struct Guild {
    uint64_t id;
    string prefix;
    uint64_t easy_role_id;
    uint64_t cargo_role_id;
};