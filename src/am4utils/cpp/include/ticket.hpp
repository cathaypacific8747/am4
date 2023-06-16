#pragma once
#include "user.hpp"

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