#include <math.h>
#include <vector>
#include <cmath>
#include "include/airport.hpp"
#include "include/route.hpp"
#include "include/enums.h"

uint16_t CargoTicket::optimal_l_real_price(float distance) {
    return floor(((0.000776321822039374 * distance + 0.860567600367807000) - 0.01) * 1.10 * 100) / 100;
}

uint16_t CargoTicket::optimal_h_real_price(float distance) {
    return floor(((0.000517742799409248 * distance + 0.256369915396414000) - 0.01) * 1.08 * 100) / 100;
}

uint16_t CargoTicket::optimal_l_easy_price(float distance) {
    return floor(((0.000948283724581252 * distance + 0.862045432642377000) - 0.01) * 1.10 * 100) / 100;
}

uint16_t CargoTicket::optimal_h_easy_price(float distance) {
    return floor(((0.000689663577640275 * distance + 0.292981124272893000) - 0.01) * 1.08 * 100) / 100;
}

uint16_t PaxTicket::optimal_y_real_price(float distance) {
    return floor((0.3 * distance + 150) * 1.10 / 10) * 10;
}

uint16_t PaxTicket::optimal_j_real_price(float distance) {
    return floor((0.6 * distance + 500) * 1.08 / 10) * 10;
}

uint16_t PaxTicket::optimal_f_real_price(float distance) {
    return floor((0.9 * distance + 1000) * 1.06 / 10) * 10;
}

uint16_t PaxTicket::optimal_y_easy_price(float distance) {
    return floor((0.4 * distance + 170) * 1.10 / 10) * 10;
}

uint16_t PaxTicket::optimal_j_easy_price(float distance) {
    return floor((0.8 * distance + 560) * 1.08 / 10) * 10;
}

uint16_t PaxTicket::optimal_f_easy_price(float distance) {
    return floor((1.2 * distance + 1200) * 1.06 / 10) * 10;
}

PaxTicket PaxTicket::from_optimal(float distance, GameMode game_mode) {
    PaxTicket ticket;
    if (game_mode == GameMode::EASY) {
        ticket.y = optimal_y_easy_price(distance);
        ticket.j = optimal_j_easy_price(distance);
        ticket.f = optimal_f_easy_price(distance);
    } else {
        ticket.y = optimal_y_real_price(distance);
        ticket.j = optimal_j_real_price(distance);
        ticket.f = optimal_f_real_price(distance);
    }
    return ticket;
};

CargoTicket CargoTicket::from_optimal(float distance, GameMode game_mode) {
    CargoTicket ticket;
    if (game_mode == GameMode::EASY) {
        ticket.l = optimal_l_easy_price(distance);
        ticket.h = optimal_h_easy_price(distance);
    } else {
        ticket.l = optimal_l_real_price(distance);
        ticket.h = optimal_h_real_price(distance);
    }
    return ticket;
};

double Route::calc_distance(double lat1, double lon1, double lat2, double lon2) {
    // NOTE: official distance uses double instead
    double dLat = (lat2 - lat1) * PI / 180.0;
    double dLon = (lon2 - lon1) * PI / 180.0;
    return 12742 * asin(sqrt(pow(sin(dLat / 2), 2) + cos(lat1 * PI / 180.0) * cos(lat2 * PI / 180.0) * pow(sin(dLon / 2), 2)));
}

double Route::calc_distance(Airport a1, Airport a2) {
    return calc_distance(a1.lat, a1.lng, a2.lat, a2.lng);
}