#include <duckdb.hpp>

#include "airport.hpp"
#include "aircraft.hpp"
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
    uint16_t f;

    PaxDemand();
    PaxDemand(uint16_t y, uint16_t j, uint16_t f);
    PaxDemand(const duckdb::DataChunk& chunk, idx_t row);
};

struct CargoDemand {
    uint32_t l;
    uint32_t h;

    CargoDemand();
    CargoDemand(uint32_t l, uint32_t h);
    CargoDemand(uint16_t y, uint16_t j);
    CargoDemand(const duckdb::DataChunk& chunk, idx_t row);
    CargoDemand(const PaxDemand& pax_demand);
};

struct Route {
    Airport origin;
    Airport destination;

    PaxDemand pax_demand;
    CargoDemand cargo_demand;

    double distance;
    bool valid = false;

    Route();

    static inline double calc_distance(double lat1, double lon1, double lat2, double lon2);
    static inline double calc_distance(const Airport& a0, const Airport& a1);
    static inline duckdb::unique_ptr<duckdb::QueryResult> Route::__get_route_result(uint16_t id0, uint16_t id1);

    static Route from_airports(const Airport& a0, const Airport& a1);
    static Route from_airports_with_aircraft(const Airport& a0, const Airport& a1, const Aircraft& ac);

    const string repr();
};