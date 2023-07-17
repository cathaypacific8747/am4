#pragma once
#include "game.hpp"

using std::string;
using std::to_string;

struct PaxTicket {
    uint16_t y;
    uint16_t j;
    uint16_t f;
    
    static PaxTicket from_optimal(double distance, User::GameMode game_mode = User::GameMode::EASY);
    static const string repr(const PaxTicket& ticket);
};

struct CargoTicket {
    float l;
    float h;

    static CargoTicket from_optimal(double distance, User::GameMode game_mode = User::GameMode::EASY);
    static const string repr(const CargoTicket& ticket);
};

struct VIPTicket {
    uint16_t y;
    uint16_t j;
    uint16_t f;
    
    static VIPTicket from_optimal(double distance);
    static const string repr(const VIPTicket& ticket);
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

#if BUILD_PYBIND == 1
#include "binder.hpp"

py::dict to_dict(const PaxTicket& ticket);
py::dict to_dict(const CargoTicket& ticket);
py::dict to_dict(const VIPTicket& ticket);
#endif