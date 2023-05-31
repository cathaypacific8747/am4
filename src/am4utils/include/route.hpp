#include "airport.hpp"
#include "enums.h"

constexpr double PI = 3.14159265358979323846;

struct PaxTicket {
    uint16_t y;
    uint16_t j;
    uint16_t f;
    
    static PaxTicket from_optimal(float distance, GameMode game_mode);
    static uint16_t optimal_y_real_price(float distance);
    static uint16_t optimal_j_real_price(float distance);
    static uint16_t optimal_f_real_price(float distance);
    static uint16_t optimal_y_easy_price(float distance);
    static uint16_t optimal_j_easy_price(float distance);
    static uint16_t optimal_f_easy_price(float distance);
};

struct CargoTicket {
    uint16_t l;
    uint16_t h;

    static CargoTicket from_optimal(float distance, GameMode game_mode);
    static uint16_t optimal_l_real_price(float distance);
    static uint16_t optimal_h_real_price(float distance);
    static uint16_t optimal_l_easy_price(float distance);
    static uint16_t optimal_h_easy_price(float distance);
};

union Ticket {
    PaxTicket pax;
    CargoTicket cargo;
};

struct PaxDemand {
    uint16_t y;
    uint16_t j;
    uint16_t d;
};

struct CargoDemand {
    uint16_t l;
    uint16_t h;
};

struct Route {
    Airport from;
    Airport to;

    Ticket ticket;
    
    double distance;

    static double calc_distance(double lat1, double lon1, double lat2, double lon2);
    static double calc_distance(Airport a0, Airport a1);
};