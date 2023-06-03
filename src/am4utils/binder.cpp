#include <pybind11/pybind11.h>
#include "include/enums.h"
#include "include/db.hpp"
#include "include/airport.hpp"
#include "include/aircraft.hpp"
#include "include/route.hpp"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#ifdef VERSION_INFO
    string version = MACRO_STRINGIFY(VERSION_INFO);
#else
    string version = "dev";
#endif

#ifdef CORE_DIR
    string core_dir = MACRO_STRINGIFY(CORE_DIR);
#else
    string core_dir = ""
#endif

namespace py = pybind11;
using namespace pybind11::literals;

PYBIND11_MODULE(_core, m) {
    py::enum_<GameMode>(m, "GameMode")
        .value("EASY", GameMode::EASY)
        .value("REALISM", GameMode::REALISM)
        .export_values();
    
    py::enum_<AircraftType>(m, "AircraftType")
        .value("PAX", AircraftType::PAX)
        .value("CARGO", AircraftType::CARGO)
        .value("VIP", AircraftType::VIP)
        .export_values();

    py::class_<PaxTicket>(m, "PaxTicket")
        .def(py::init<>())
        .def_readwrite("y", &PaxTicket::y)
        .def_readwrite("j", &PaxTicket::j)
        .def_readwrite("f", &PaxTicket::f)
        .def("__repr__",
            [](const PaxTicket &a) {
                return "<PaxTicket y=" + std::to_string(a.y) + " j=" + std::to_string(a.j) + " f=" + std::to_string(a.f) + ">";
            }
        );

    py::class_<CargoTicket>(m, "CargoTicket")
        .def(py::init<>())
        .def_readwrite("l", &CargoTicket::l)
        .def_readwrite("h", &CargoTicket::h)
        .def("__repr__",
            [](const CargoTicket &a) {
                return "<CargoTicket l=" + std::to_string(a.l) + " h=" + std::to_string(a.h) + ">";
            }
        );
    
    py::class_<VIPTicket>(m, "VIPTicket")
        .def(py::init<>())
        .def_readwrite("y", &VIPTicket::y)
        .def_readwrite("j", &VIPTicket::j)
        .def_readwrite("f", &VIPTicket::f)
        .def("__repr__",
            [](const VIPTicket &a) {
                return "<VIPTicket y=" + std::to_string(a.y) + " j=" + std::to_string(a.j) + " f=" + std::to_string(a.f) + ">";
            }
        );
    
    m.def_submodule("route")
        .def("create_optimal_pax_ticket", &PaxTicket::from_optimal, "distance"_a, "game_mode"_a = GameMode::EASY)
        .def("create_optimal_cargo_ticket", &CargoTicket::from_optimal, "distance"_a, "game_mode"_a = GameMode::EASY);

    m.def_submodule("db")
        .def("init", &init)
        .def("_debug_query", &_debug_query);

    m.attr("__version__") = version;
    m.attr("__coredir__") = core_dir;
}