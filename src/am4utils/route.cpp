#include <math.h>
#include <vector>
#include "include/route.hpp"

int optimal_l_real_price(float distance) {
    return floor(((0.000776321822039374 * distance + 0.860567600367807000) - 0.01) * 1.10 * 100) / 100;
}

int optimal_h_real_price(float distance) {
    return floor(((0.000517742799409248 * distance + 0.256369915396414000) - 0.01) * 1.08 * 100) / 100;
}

int optimal_l_easy_price(float distance) {
    return floor(((0.000948283724581252 * distance + 0.862045432642377000) - 0.01) * 1.10 * 100) / 100;
}

int optimal_h_easy_price(float distance) {
    return floor(((0.000689663577640275 * distance + 0.292981124272893000) - 0.01) * 1.08 * 100) / 100;
}

int optimal_y_real_price(float distance) {
    return floor((0.3 * distance + 150) * 1.10 / 10) * 10;
}

int optimal_j_real_price(float distance) {
    return floor((0.6 * distance + 500) * 1.08 / 10) * 10;
}

int optimal_f_real_price(float distance) {
    return floor((0.9 * distance + 1000) * 1.06 / 10) * 10;
}

int optimal_y_easy_price(float distance) {
    return floor((0.4 * distance + 170) * 1.10 / 10) * 10;
}

int optimal_j_easy_price(float distance) {
    return floor((0.8 * distance + 560) * 1.08 / 10) * 10;
}

int optimal_f_easy_price(float distance) {
    return floor((1.2 * distance + 1200) * 1.06 / 10) * 10;
}

PaxTicket create_pax_ticket(float distance, bool is_easy) {
    PaxTicket ticket;
    if (is_easy) {
        ticket.y_price = optimal_y_easy_price(distance);
        ticket.j_price = optimal_j_easy_price(distance);
        ticket.f_price = optimal_f_easy_price(distance);
    } else {
        ticket.y_price = optimal_y_real_price(distance);
        ticket.j_price = optimal_j_real_price(distance);
        ticket.f_price = optimal_f_real_price(distance);
    }
    return ticket;
};

CargoTicket create_cargo_ticket(float distance, bool is_easy) {
    CargoTicket ticket;
    if (is_easy) {
        ticket.l_price = optimal_l_easy_price(distance);
        ticket.h_price = optimal_h_easy_price(distance);
    } else {
        ticket.l_price = optimal_l_real_price(distance);
        ticket.h_price = optimal_h_real_price(distance);
    }
    return ticket;
};