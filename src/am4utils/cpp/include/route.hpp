#include <duckdb.hpp>

#include "airport.hpp"
#include "aircraft.hpp"
#include "user.hpp"

constexpr double PI = 3.14159265358979323846;

struct PaxTicket {
    uint16_t y;
    uint16_t j;
    uint16_t f;
    
    static PaxTicket from_optimal(float distance, User::GameMode game_mode = User::GameMode::EASY);
};

struct CargoTicket {
    float l;
    float h;

    static CargoTicket from_optimal(float distance, User::GameMode game_mode = User::GameMode::EASY);
};

struct VIPTicket {
    uint16_t y;
    uint16_t j;
    uint16_t f;
    
    static VIPTicket from_optimal(float distance);
};

union Ticket {
    PaxTicket pax_ticket;
    CargoTicket cargo_ticket;
    VIPTicket vip_ticket;

    Ticket() {}
    Ticket(const PaxTicket& pax_ticket) : pax_ticket(pax_ticket) {}
    Ticket(const CargoTicket& cargo_ticket) : cargo_ticket(cargo_ticket) {}
    Ticket(const VIPTicket& vip_ticket) : vip_ticket(vip_ticket) {}
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

    PurchasedAircraft aircraft;
    Ticket ticket;

    double direct_distance;
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

    static inline CargoConfig calc_l_conf(const CargoDemand& d_pf, uint32_t capacity);
    static inline CargoConfig calc_h_conf(const CargoDemand& d_pf, uint32_t capacity);

    static PaxConfig Route::calc_pax_conf(const PaxDemand& pax_demand, uint16_t capacity, float distance, uint16_t trips_per_day = 1, User::GameMode game_mode = User::GameMode::EASY);
    static CargoConfig Route::calc_cargo_conf(const CargoDemand& cargo_demand, uint32_t capacity, uint16_t trips_per_day = 1, uint8_t l_training = 0);


    static Route from_airports(const Airport& a0, const Airport& a1);
    static Route from_airports_with_aircraft(const Airport& a0, const Airport& a1, const Aircraft& ac, uint16_t trips_per_day = 1, User::GameMode game_mode = User::GameMode::EASY);

    const string repr();
};