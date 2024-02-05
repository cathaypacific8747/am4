#include "include/ticket.hpp"
#include <cmath>

PaxTicket PaxTicket::from_optimal(double distance, User::GameMode game_mode) {
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
}

CargoTicket CargoTicket::from_optimal(double distance, User::GameMode game_mode) {
    CargoTicket ticket;
    if (game_mode == User::GameMode::EASY) {
        ticket.l = floorf(static_cast<float>(1.10 * (0.0948283724581252 * distance + 85.2045432642377000))) / 100;
        ticket.h = floorf(static_cast<float>(1.08 * (0.0689663577640275 * distance + 28.2981124272893000))) / 100;
    } else {
        ticket.l = floorf(static_cast<float>(1.10 * (0.0776321822039374 * distance + 85.0567600367807000))) / 100;
        ticket.h = floorf(static_cast<float>(1.08 * (0.0517742799409248 * distance + 24.6369915396414000))) / 100;
    }
    return ticket;
}

VIPTicket VIPTicket::from_optimal(double distance) {
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

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict to_dict(const PaxTicket& ticket) {
    return py::dict("y"_a=ticket.y, "j"_a=ticket.j, "f"_a=ticket.f);
}

py::dict to_dict(const CargoTicket& ticket) {
    return py::dict("l"_a=ticket.l, "h"_a=ticket.h);
}

py::dict to_dict(const VIPTicket& ticket) {
    return py::dict("y"_a=ticket.y, "j"_a=ticket.j, "f"_a=ticket.f);
}

void pybind_init_ticket(py::module_& m) {
    py::module_ m_ticket = m.def_submodule("ticket");
    
    py::class_<PaxTicket>(m_ticket, "PaxTicket")
        .def_readonly("y", &PaxTicket::y)
        .def_readonly("j", &PaxTicket::j)
        .def_readonly("f", &PaxTicket::f)
        .def_static("from_optimal", &PaxTicket::from_optimal, "distance"_a, py::arg_v("game_mode", User::GameMode::EASY, "am4utils._core.game.User.GameMode.EASY")) // https://pybind11.readthedocs.io/en/stable/advanced/functions.html?highlight=default%20argument#default-arguments-revisited
        .def("__repr__", &PaxTicket::repr)
        .def("to_dict", py::overload_cast<const PaxTicket&>(&to_dict));

    py::class_<CargoTicket>(m_ticket, "CargoTicket")
        .def_readonly("l", &CargoTicket::l)
        .def_readonly("h", &CargoTicket::h)
        .def_static("from_optimal", &PaxTicket::from_optimal, "distance"_a, py::arg_v("game_mode", User::GameMode::EASY, "am4utils._core.game.User.GameMode.EASY"))
        .def("__repr__", &CargoTicket::repr)
        .def("to_dict", py::overload_cast<const CargoTicket&>(&to_dict));
    
    py::class_<VIPTicket>(m_ticket, "VIPTicket")
        .def_readonly("y", &VIPTicket::y)
        .def_readonly("j", &VIPTicket::j)
        .def_readonly("f", &VIPTicket::f)
        .def_static("from_optimal", &VIPTicket::from_optimal, "distance"_a)
        .def("__repr__", &VIPTicket::repr)
        .def("to_dict", py::overload_cast<const VIPTicket&>(&to_dict));
}
#endif