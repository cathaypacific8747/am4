#pragma once
#include <string>

struct User {
    enum class GameMode {
        EASY,
        REALISM
    };

    uint64_t id;
    uint32_t game_id;
    std::string ign;
    GameMode mode;
    uint8_t l_training; // 0-6
    uint8_t h_training; // 0-6
    uint16_t fuel_price; // 0-3000
    uint8_t co2_price; // 0-200
    uint8_t fuel_training; // 0-3
    uint8_t co2_training; // 0-5
    uint8_t reputation; // 0-100

    // TODO: add algorithm overrides, use estimation
};

struct Guild {
    uint64_t id;
    std::string prefix;
    uint64_t easy_role_id;
    uint64_t cargo_role_id;
};