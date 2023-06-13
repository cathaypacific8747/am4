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

namespace py = pybind11;
using namespace pybind11::literals;

PYBIND11_MODULE(_core, m) {
    py::module_ m_db = m.def_submodule("db", "Database");
    py::module_ m_ac = m.def_submodule("aircraft", "Aircraft");
    py::module_ m_ap = m.def_submodule("airport", "Airport");
    py::module_ m_route = m.def_submodule("route", "Route");

    // needs to be defined before classes for default arguments to work
    py::enum_<GameMode>(m, "GameMode")
        .value("EASY", GameMode::EASY)
        .value("REALISM", GameMode::REALISM);

    py::enum_<AircraftType>(m_ac, "AircraftType")
        .value("PAX", AircraftType::PAX)
        .value("CARGO", AircraftType::CARGO)
        .value("VIP", AircraftType::VIP);
    
    py::enum_<PaxConfigAlgorithm>(m_ac, "PaxConfigAlgorithm")
        .value("FJY", PaxConfigAlgorithm::FJY).value("FYJ", PaxConfigAlgorithm::FYJ)
        .value("JFY", PaxConfigAlgorithm::JFY).value("JYF", PaxConfigAlgorithm::JYF)
        .value("YJF", PaxConfigAlgorithm::YJF).value("YFJ", PaxConfigAlgorithm::YFJ);


    /*** DATABASE ***/
    m_db
        .def("init", &init)
        .def("_debug_query", &_debug_query);

    py::register_exception<DatabaseException>(m_db, "DatabaseException");


    /*** AIRCRAFT ***/
    py::class_<Aircraft>(m_ac, "Aircraft")
        .def(py::init<>())
        .def_readonly("id", &Aircraft::id)
        .def_readonly("shortname", &Aircraft::shortname)
        .def_readonly("manufacturer", &Aircraft::manufacturer)
        .def_readonly("name", &Aircraft::name)
        .def_readonly("type", &Aircraft::type)
        .def_readonly("priority", &Aircraft::priority)
        .def_readonly("eid", &Aircraft::eid)
        .def_readonly("ename", &Aircraft::ename)
        .def_readonly("speed", &Aircraft::speed)
        .def_readonly("fuel", &Aircraft::fuel)
        .def_readonly("co2", &Aircraft::co2)
        .def_readonly("cost", &Aircraft::cost)
        .def_readonly("capacity", &Aircraft::capacity)
        .def_readonly("rwy", &Aircraft::rwy)
        .def_readonly("check_cost", &Aircraft::check_cost)
        .def_readonly("range", &Aircraft::range)
        .def_readonly("ceil", &Aircraft::ceil)
        .def_readonly("maint", &Aircraft::maint)
        .def_readonly("pilots", &Aircraft::pilots)
        .def_readonly("crew", &Aircraft::crew)
        .def_readonly("engineers", &Aircraft::engineers)
        .def_readonly("technicians", &Aircraft::technicians)
        .def_readonly("img", &Aircraft::img)
        .def_readonly("wingspan", &Aircraft::wingspan)
        .def_readonly("length", &Aircraft::length)
        .def_readonly("valid", &Aircraft::valid)
        .def_static("_from_id", &Aircraft::_from_id, "id"_a, "priority"_a = 0)
        .def_static("_from_shortname", &Aircraft::_from_shortname, "s"_a, "priority"_a = 0)
        .def_static("_from_name", &Aircraft::_from_name, "s"_a, "priority"_a = 0)
        .def_static("_from_all", &Aircraft::_from_all, "s"_a, "priority"_a = 0)
        .def_static("from_auto", &Aircraft::from_auto, "s"_a)
        .def("__repr__", &Aircraft::repr);
    
    py::class_<PurchasedAircraft>(m_ac, "PurchasedAircraft")
        .def(py::init<>())
        .def_readonly("aircraft", &PurchasedAircraft::aircraft)
        .def_readonly("config", &PurchasedAircraft::config);
    
    py::class_<PurchasedAircaftConfig>(m_ac, "PurchasedAircraftConfig")
        .def(py::init<>())
        .def_readonly("pax_config", &PurchasedAircaftConfig::pax_config)
        .def_readonly("cargo_config", &PurchasedAircaftConfig::cargo_config);
    
    py::class_<PaxConfig>(m_ac, "PaxConfig")
        .def(py::init<>())
        .def_readonly("y", &PaxConfig::y)
        .def_readonly("j", &PaxConfig::j)
        .def_readonly("f", &PaxConfig::f)
        .def_readonly("valid", &PaxConfig::valid)
        .def_readonly("algorithm", &PaxConfig::algorithm);

    py::class_<CargoConfig>(m_ac, "CargoConfig")
        .def(py::init<>())
        .def_readonly("l", &CargoConfig::l)
        .def_readonly("h", &CargoConfig::h)
        .def_readonly("valid", &CargoConfig::valid);

    py::register_exception<AircraftNotFoundException>(m_ac, "AircraftNotFoundException");


    /*** AIRPORT ***/
    py::class_<Airport>(m_ap, "Airport")
        .def(py::init<>())
        .def_readonly("id", &Airport::id)
        .def_readonly("name", &Airport::name)
        .def_readonly("fullname", &Airport::fullname)
        .def_readonly("country", &Airport::country)
        .def_readonly("continent", &Airport::continent)
        .def_readonly("iata", &Airport::iata)
        .def_readonly("icao", &Airport::icao)
        .def_readonly("lat", &Airport::lat)
        .def_readonly("lng", &Airport::lng)
        .def_readonly("rwy", &Airport::rwy)
        .def_readonly("market", &Airport::market)
        .def_readonly("hub_cost", &Airport::hub_cost)
        .def_readonly("rwy_codes", &Airport::rwy_codes)
        .def_readonly("valid", &Airport::valid)
        .def_static("_from_id", &Airport::_from_id, "id"_a)
        .def_static("_from_iata", &Airport::_from_iata, "s"_a)
        .def_static("_from_icao", &Airport::_from_icao, "s"_a)
        .def_static("_from_name", &Airport::_from_name, "s"_a)
        .def_static("_from_all", &Airport::_from_all, "s"_a)
        .def_static("from_auto", &Airport::from_auto, "s"_a)
        .def("__repr__", &Airport::repr);

    py::register_exception<AirportNotFoundException>(m_ap, "AirportNotFoundException");


    /*** ROUTE ***/
    py::class_<Route>(m_route, "Route")
        .def(py::init<>())
        .def_readonly("origin", &Route::origin)
        .def_readonly("destination", &Route::destination)
        .def_readonly("pax_demand", &Route::pax_demand)
        .def_readonly("cargo_demand", &Route::cargo_demand)
        .def_readonly("purchased_aircraft", &Route::purchased_aircraft)
        .def_readonly("ticket", &Route::ticket)
        .def_readonly("distance", &Route::distance)
        .def_readonly("valid", &Route::valid)
        .def_static("create_optimal_pax_ticket", &PaxTicket::from_optimal, "distance"_a, "game_mode"_a)
        .def_static("create_optimal_cargo_ticket", &CargoTicket::from_optimal, "distance"_a, "game_mode"_a)
        .def_static("from_airports", &Route::from_airports, "ap1"_a, "ap2"_a)
        .def_static("from_airports_with_aircraft", &Route::from_airports_with_aircraft, "ap1"_a, "ap2"_a, "ac"_a, "trips_per_day"_a = 1, "game_mode"_a = GameMode::EASY)
        .def("__repr__", &Route::repr);
        

    py::class_<PaxTicket>(m_route, "PaxTicket")
        .def(py::init<>())
        .def_readonly("y", &PaxTicket::y)
        .def_readonly("j", &PaxTicket::j)
        .def_readonly("f", &PaxTicket::f)
        .def("__repr__",
            [](const PaxTicket &a) {
                return "<PaxTicket y=" + std::to_string(a.y) + " j=" + std::to_string(a.j) + " f=" + std::to_string(a.f) + ">";
            }
        );

    py::class_<CargoTicket>(m_route, "CargoTicket")
        .def(py::init<>())
        .def_readonly("l", &CargoTicket::l)
        .def_readonly("h", &CargoTicket::h)
        .def("__repr__",
            [](const CargoTicket &a) {
                return "<CargoTicket l=" + std::to_string(a.l) + " h=" + std::to_string(a.h) + ">";
            }
        );
    
    py::class_<VIPTicket>(m_route, "VIPTicket")
        .def(py::init<>())
        .def_readonly("y", &VIPTicket::y)
        .def_readonly("j", &VIPTicket::j)
        .def_readonly("f", &VIPTicket::f)
        .def("__repr__",
            [](const VIPTicket &a) {
                return "<VIPTicket y=" + std::to_string(a.y) + " j=" + std::to_string(a.j) + " f=" + std::to_string(a.f) + ">";
            }
        );
    
    py::class_<Ticket>(m_route, "Ticket")
        .def(py::init<>())
        .def_readonly("pax_ticket", &Ticket::pax_ticket)
        .def_readonly("cargo_ticket", &Ticket::cargo_ticket)
        .def_readonly("vip_ticket", &Ticket::vip_ticket);
    
    py::class_<PaxDemand>(m_route, "PaxDemand")
        .def(py::init<>())
        .def_readonly("y", &PaxDemand::y)
        .def_readonly("j", &PaxDemand::j)
        .def_readonly("f", &PaxDemand::f)
        .def("__repr__",
            [](const PaxDemand &a) {
                return "<PaxDemand y=" + std::to_string(a.y) + " j=" + std::to_string(a.j) + " f=" + std::to_string(a.f) + ">";
            }
        );
    
    py::class_<CargoDemand>(m_route, "CargoDemand")
        .def(py::init<>())
        .def_readonly("l", &CargoDemand::l)
        .def_readonly("h", &CargoDemand::h)
        .def("__repr__",
            [](const CargoDemand &a) {
                return "<CargoDemand l=" + std::to_string(a.l) + " h=" + std::to_string(a.h) + ">";
            }
        );
    
    m.attr("__version__") = version;
}