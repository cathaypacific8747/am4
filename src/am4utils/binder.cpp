#include <pybind11/pybind11.h>
#include "include/enums.h"
#include "include/db.hpp"
#include "include/airport.hpp"
#include "include/aircraft.hpp"
#include "include/route.hpp"

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
    m.def_submodule("db")
        .def("init", &init)
        .def("_debug_query", &_debug_query);
    
    m.def_submodule("airport")
        .def("from_id", &Airport::from_id, "id"_a);

    m.def_submodule("aircraft");

    m.def_submodule("route")
        .def("create_optimal_pax_ticket", &PaxTicket::from_optimal, "distance"_a, "game_mode"_a)
        .def("create_optimal_cargo_ticket", &CargoTicket::from_optimal, "distance"_a, "game_mode"_a)
        .def("from_airports", &Route::from_airports, "a1"_a, "a2"_a);
    
    // airport
    py::class_<Airport>(m, "Airport")
        .def(py::init<>())
        .def_readwrite("id", &Airport::id)
        .def_readwrite("name", &Airport::name)
        .def_readwrite("fullname", &Airport::fullname)
        .def_readwrite("country", &Airport::country)
        .def_readwrite("continent", &Airport::continent)
        .def_readwrite("iata", &Airport::iata)
        .def_readwrite("icao", &Airport::icao)
        .def_readwrite("lat", &Airport::lat)
        .def_readwrite("lng", &Airport::lng)
        .def_readwrite("rwy", &Airport::rwy)
        .def_readwrite("market", &Airport::market)
        .def_readwrite("hub_cost", &Airport::hub_cost)
        .def_readwrite("rwy_codes", &Airport::rwy_codes)
        .def_readwrite("valid", &Airport::valid)
        .def("__repr__",
            [](const Airport &a) {
                return "<Airport id=" + std::to_string(a.id) + " name=" + a.name + " fullname=" + a.fullname + " country=" + a.country + " continent=" + a.continent + " iata=" + a.iata + " icao=" + a.icao + " lat=" + std::to_string(a.lat) + " lng=" + std::to_string(a.lng) + " rwy=" + std::to_string(a.rwy) + " market=" + std::to_string(a.market) + " hub_cost=" + std::to_string(a.hub_cost) + " rwy_codes=" + a.rwy_codes + " valid=" + std::to_string(a.valid) + ">";
            }
        );

    // route, todo: proper repr!
    py::class_<Route>(m, "Route")
        .def(py::init<>())
        .def_readwrite("origin", &Route::origin)
        .def_readwrite("destination", &Route::destination)
        .def_readwrite("pax_demand", &Route::pax_demand)
        .def_readwrite("distance", &Route::distance)
        .def_readwrite("valid", &Route::valid)
        .def("__repr__",
            [](const Route &a) {
                return "<Route distance=" + std::to_string(a.distance) + " valid=" + std::to_string(a.valid) + ">";
            }
        );
        

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
    
    py::class_<PaxDemand>(m, "PaxDemand")
        .def(py::init<>())
        .def_readwrite("y", &PaxDemand::y)
        .def_readwrite("j", &PaxDemand::j)
        .def_readwrite("f", &PaxDemand::f)
        .def("__repr__",
            [](const PaxDemand &a) {
                return "<PaxDemand y=" + std::to_string(a.y) + " j=" + std::to_string(a.j) + " f=" + std::to_string(a.f) + ">";
            }
        );
    
    py::class_<CargoDemand>(m, "CargoDemand")
        .def(py::init<>())
        .def_readwrite("l", &CargoDemand::l)
        .def_readwrite("h", &CargoDemand::h)
        .def("__repr__",
            [](const CargoDemand &a) {
                return "<CargoDemand l=" + std::to_string(a.l) + " h=" + std::to_string(a.h) + ">";
            }
        );
    

    // enums
    py::enum_<GameMode>(m, "GameMode")
        .value("EASY", GameMode::EASY)
        .value("REALISM", GameMode::REALISM)
        .export_values();
    
    py::enum_<AircraftType>(m, "AircraftType")
        .value("PAX", AircraftType::PAX)
        .value("CARGO", AircraftType::CARGO)
        .value("VIP", AircraftType::VIP)
        .export_values();
    
    py::register_exception<DatabaseException>(m, "DatabaseException");

    m.attr("__version__") = version;
    m.attr("__coredir__") = core_dir;
}