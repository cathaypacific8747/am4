#include "include/binder.hpp"

#include "include/db.hpp"
#include "include/game.hpp"
#include "include/ticket.hpp"
#include "include/demand.hpp"

#include "include/airport.hpp"
#include "include/aircraft.hpp"
#include "include/route.hpp"

#include "include/log.hpp"

void pybind_init_db(py::module_&);
void pybind_init_game(py::module_&);
void pybind_init_ticket(py::module_&);
void pybind_init_demand(py::module_&);
void pybind_init_airport(py::module_&);
void pybind_init_aircraft(py::module_&);
void pybind_init_route(py::module_&);
void pybind_init_log(py::module_&);

PYBIND11_MODULE(_core, m) {
    pybind_init_db(m);
    pybind_init_game(m);
    pybind_init_ticket(m);
    pybind_init_demand(m);
    pybind_init_airport(m);
    pybind_init_aircraft(m);
    pybind_init_route(m);
    pybind_init_log(m);

    #ifdef VERSION_INFO
        m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
    #endif
}