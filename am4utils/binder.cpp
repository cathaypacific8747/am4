#include <pybind11/pybind11.h>
#include "route.hpp"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(am4utils, m) {
    m.def("optimal_l_real_price", &optimal_l_real_price);
    m.def("optimal_h_real_price", &optimal_h_real_price);
    m.def("optimal_l_easy_price", &optimal_l_easy_price);
    m.def("optimal_h_easy_price", &optimal_h_easy_price);
    m.def("optimal_y_real_price", &optimal_y_real_price);
    m.def("optimal_j_real_price", &optimal_j_real_price);
    m.def("optimal_f_real_price", &optimal_f_real_price);
    m.def("optimal_y_easy_price", &optimal_y_easy_price);
    m.def("optimal_j_easy_price", &optimal_j_easy_price);
    m.def("optimal_f_easy_price", &optimal_f_easy_price);

    
    py::class_<PaxTicket>(m, "PaxTicket")
        .def(py::init<>())
        .def_readwrite("y_price", &PaxTicket::y_price)
        .def_readwrite("j_price", &PaxTicket::j_price)
        .def_readwrite("f_price", &PaxTicket::f_price);

    py::class_<CargoTicket>(m, "CargoTicket")
        .def(py::init<>())
        .def_readwrite("l_price", &CargoTicket::l_price)
        .def_readwrite("h_price", &CargoTicket::h_price);

    m.def("create_pax_ticket", &create_pax_ticket, py::arg("distance"), py::arg("is_easy"));
    m.def("create_cargo_ticket", &create_cargo_ticket, py::arg("distance"), py::arg("is_easy"));


    m.attr("__version__") = "0.0.1";
}