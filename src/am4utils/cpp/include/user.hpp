// # this assumes all strings supplied are SQL-injection proof, and already checked for bounds.
// cdef struct us_det:
//     int discordId
//     int gameId
//     char* ign
//     #
//     char* mode # 'e', 'r', 'unknown'
//     char* paxMode # 'y', 'f', 'brute'
//     char* cargoMode # 'l', 'brute'
//     int lTraining # 0-6
//     int hTraining # 0-6
//     int fuelPrice # 0-3000
//     int co2Price # 0-200
//     int fuelTraining # 0-3
//     int co2Training # 0-5
//     int useEstimation # 0/1
//     int reputation # 0-100

#include <string>
#include "enums.h"

struct User {
    uint64_t id;
    uint32_t game_id;
    std::string ign;
    GameMode mode;
    // string pax_mode;
    // string cargo_mode;
    uint8_t l_training; // 0-6
    uint8_t h_training; // 0-6
    uint16_t fuel_price; // 0-3000
    uint8_t co2_price; // 0-200
    uint8_t fuel_training; // 0-3
    uint8_t co2_training; // 0-5
    // bool use_estimation;
    uint8_t reputation; // 0-100
};

struct Guild {
    uint64_t id;
    std::string prefix;
    uint64_t easy_role_id;
    uint64_t cargo_role_id;
};