#include "airport.hpp"
#include "enums.h"

constexpr double PI = 3.14159265358979323846;

struct PaxTicket {
    uint16_t y;
    uint16_t j;
    uint16_t f;
    
    static PaxTicket from_optimal(float distance, GameMode game_mode);
};

struct CargoTicket {
    float l;
    float h;

    static CargoTicket from_optimal(float distance, GameMode game_mode);
};

struct VIPTicket {
    uint16_t y;
    uint16_t j;
    uint16_t f;
    
    static VIPTicket from_optimal(float distance);
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

    double distance;

    static double calc_distance(double lat1, double lon1, double lat2, double lon2);
    static double calc_distance(Airport a0, Airport a1);
};