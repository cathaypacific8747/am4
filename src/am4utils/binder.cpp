#include <pybind11/pybind11.h>
#include "include/route.hpp"
#include "include/airport.hpp"
#include "include/db.hpp"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.def_submodule("route")
        .def("optimal_l_real_price", &optimal_l_real_price)
        .def("optimal_h_real_price", &optimal_h_real_price)
        .def("optimal_l_easy_price", &optimal_l_easy_price)
        .def("optimal_h_easy_price", &optimal_h_easy_price)
        .def("optimal_y_real_price", &optimal_y_real_price)
        .def("optimal_j_real_price", &optimal_j_real_price)
        .def("optimal_f_real_price", &optimal_f_real_price)
        .def("optimal_y_easy_price", &optimal_y_easy_price)
        .def("optimal_j_easy_price", &optimal_j_easy_price)
        .def("optimal_f_easy_price", &optimal_f_easy_price);
    
    py::class_<PaxTicket>(m, "PaxTicket")
        .def(py::init<>())
        .def_readwrite("y_price", &PaxTicket::y_price)
        .def_readwrite("j_price", &PaxTicket::j_price)
        .def_readwrite("f_price", &PaxTicket::f_price);

    py::class_<CargoTicket>(m, "CargoTicket")
        .def(py::init<>())
        .def_readwrite("l_price", &CargoTicket::l_price)
        .def_readwrite("h_price", &CargoTicket::h_price);

    m.def("create_pax_ticket", &create_pax_ticket);
    m.def("create_cargo_ticket", &create_cargo_ticket);

    m.def_submodule("db")
        .def("init", &init)
        .def("_query", &_query);

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif

#ifdef CORE_DIR
    m.attr("__coredir__") = MACRO_STRINGIFY(CORE_DIR);
#else
    m.attr("__coredir__") = "";
#endif
}