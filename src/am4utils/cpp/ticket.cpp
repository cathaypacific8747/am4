#include "include/ticket.hpp"
#include <cmath>

PaxTicket PaxTicket::from_optimal(float distance, User::GameMode game_mode) {
    PaxTicket ticket;
    if (game_mode == User::GameMode::EASY) {
        ticket.y = (uint16_t)(1.10 * (0.4 * distance + 170)) - 2;
        ticket.j = (uint16_t)(1.08 * (0.8 * distance + 560)) - 2;
        ticket.f = (uint16_t)(1.06 * (1.2 * distance + 1200)) - 2;
    } else {
        ticket.y = (uint16_t)(1.10 * (0.3 * distance + 150)) - 2;
        ticket.j = (uint16_t)(1.08 * (0.6 * distance + 500)) - 2;
        ticket.f = (uint16_t)(1.06 * (0.9 * distance + 1000)) - 2;
    }
    return ticket;
};

CargoTicket CargoTicket::from_optimal(float distance, User::GameMode game_mode) {
    CargoTicket ticket;
    if (game_mode == User::GameMode::EASY) {
        ticket.l = floorf(1.10 * (0.0948283724581252 * distance + 85.2045432642377000)) / 100;
        ticket.h = floorf(1.08 * (0.0689663577640275 * distance + 28.2981124272893000)) / 100;
    } else {
        ticket.l = floorf(1.10 * (0.0776321822039374 * distance + 85.0567600367807000)) / 100;
        ticket.h = floorf(1.08 * (0.0517742799409248 * distance + 24.6369915396414000)) / 100;
    }
    return ticket;
};

VIPTicket VIPTicket::from_optimal(float distance) {
    VIPTicket ticket;
    ticket.y = (uint16_t)(1.22 * 1.7489 * (0.4 * distance + 170)) - 2;
    ticket.j = (uint16_t)(1.20 * 1.7489 * (0.8 * distance + 560)) - 2;
    ticket.f = (uint16_t)(1.17 * 1.7489 * (1.2 * distance + 1200)) - 2;
    return ticket;
}

const string PaxTicket::repr(const PaxTicket& ticket) {
    return "<PaxTicket " + to_string(ticket.y) + "|" + to_string(ticket.j) + "|" + to_string(ticket.f) + ">";
}

const string CargoTicket::repr(const CargoTicket& ticket) {
    return "<CargoTicket " + to_string(ticket.l) + "|" + to_string(ticket.h) + ">";
}

const string VIPTicket::repr(const VIPTicket& ticket) {
    return "<VIPTicket " + to_string(ticket.y) + "|" + to_string(ticket.j) + "|" + to_string(ticket.f) + ">";
}