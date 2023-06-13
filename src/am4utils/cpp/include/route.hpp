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
    // Airport stopover;
    Airport destination;

    PaxDemand pax_demand;
    CargoDemand cargo_demand;

    PurchasedAircraft routed_aircraft;

    double distance;
    bool valid = false;
    // bool has_stopover = false;
    // double stopover_extra_distance = 0.0;

    Route();

    static inline double calc_distance(double lat1, double lon1, double lat2, double lon2);
    static inline double calc_distance(const Airport& a0, const Airport& a1);
    static inline duckdb::unique_ptr<duckdb::QueryResult> __get_route_result(uint16_t id0, uint16_t id1);

    static inline PaxConfig calc_fjy_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_fyj_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_jfy_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_jyf_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_yfj_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_yjf_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);

    static PaxConfig Route::calc_pax_conf(const PaxDemand& pax_demand, uint16_t capacity, float distance, uint16_t trips_per_day = 1, GameMode game_mode = GameMode::EASY);
    static CargoConfig Route::calc_cargo_conf(const CargoDemand& cargo_demand, uint32_t capacity, uint16_t trips_per_day = 1, uint8_t l_training = 0);


    static Route from_airports(const Airport& a0, const Airport& a1);
    static Route from_airports_with_aircraft(const Airport& a0, const Airport& a1, const Aircraft& ac, uint16_t trips_per_day = 1);

    const string repr();
};