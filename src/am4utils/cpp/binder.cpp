#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "include/db.hpp"
#include "include/user.hpp"
#include "include/ticket.hpp"
#include "include/demand.hpp"

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
using std::string;

PYBIND11_MODULE(_core, m) {
    py::module_ m_db = m.def_submodule("db");
    py::module_ m_user = m.def_submodule("user");
    py::module_ m_ticket = m.def_submodule("ticket");
    py::module_ m_demand = m.def_submodule("demand");
    py::module_ m_ac = m.def_submodule("aircraft");
    py::module_ m_ap = m.def_submodule("airport");
    py::module_ m_route = m.def_submodule("route");

    /*** DATABASE ***/
    m_db
        .def("init", &init)
        .def("_debug_query", &_debug_query);

    py::register_exception<DatabaseException>(m_db, "DatabaseException");

    /*** USER ***/
    py::enum_<User::GameMode>(m_user, "GameMode")
        .value("EASY", User::GameMode::EASY)
        .value("REALISM", User::GameMode::REALISM);

    /*** TICKET ***/
    py::class_<PaxTicket>(m_ticket, "PaxTicket")
        .def_readonly("y", &PaxTicket::y)
        .def_readonly("j", &PaxTicket::j)
        .def_readonly("f", &PaxTicket::f)
        .def_static("from_optimal", &PaxTicket::from_optimal, "distance"_a, "game_mode"_a = User::GameMode::EASY)
        .def("__repr__", &PaxTicket::repr);

    py::class_<CargoTicket>(m_ticket, "CargoTicket")
        .def_readonly("l", &CargoTicket::l)
        .def_readonly("h", &CargoTicket::h)
        .def_static("from_optimal", &CargoTicket::from_optimal, "distance"_a, "game_mode"_a = User::GameMode::EASY)
        .def("__repr__", &CargoTicket::repr);
    
    py::class_<VIPTicket>(m_ticket, "VIPTicket")
        .def_readonly("y", &VIPTicket::y)
        .def_readonly("j", &VIPTicket::j)
        .def_readonly("f", &VIPTicket::f)
        .def_static("from_optimal", &VIPTicket::from_optimal, "distance"_a)
        .def("__repr__", &VIPTicket::repr);
    
    py::class_<Ticket>(m_ticket, "Ticket")
        .def_readonly("pax_ticket", &Ticket::pax_ticket)
        .def_readonly("cargo_ticket", &Ticket::cargo_ticket)
        .def_readonly("vip_ticket", &Ticket::vip_ticket);
    

    /*** DEMAND ***/
    py::class_<PaxDemand>(m_demand, "PaxDemand")
        .def_readonly("y", &PaxDemand::y)
        .def_readonly("j", &PaxDemand::j)
        .def_readonly("f", &PaxDemand::f)
        .def("__repr__", &PaxDemand::repr);
    
    py::class_<CargoDemand>(m_demand, "CargoDemand")
        .def_readonly("l", &CargoDemand::l)
        .def_readonly("h", &CargoDemand::h)
        .def("__repr__", &CargoDemand::repr);


    /*** AIRCRAFT ***/
    py::class_<Aircraft, std::shared_ptr<Aircraft>> ac_class(m_ac, "Aircraft");
    py::enum_<Aircraft::Type>(ac_class, "Type")
        .value("PAX", Aircraft::Type::PAX)
        .value("CARGO", Aircraft::Type::CARGO)
        .value("VIP", Aircraft::Type::VIP);

    ac_class
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
        .def("__repr__", &Aircraft::repr);
    
    py::enum_<Aircraft::SearchType>(ac_class, "SearchType")
        .value("ALL", Aircraft::SearchType::ALL)
        .value("ID", Aircraft::SearchType::ID)
        .value("SHORTNAME", Aircraft::SearchType::SHORTNAME)
        .value("NAME", Aircraft::SearchType::NAME);

    py::class_<Aircraft::ParseResult>(ac_class, "ParseResult")
        .def(py::init<Aircraft::SearchType, const std::string&>())
        .def_readonly("search_type", &Aircraft::ParseResult::search_type)
        .def_readonly("search_str", &Aircraft::ParseResult::search_str);

    py::class_<Aircraft::SearchResult>(ac_class, "SearchResult")
        .def(py::init<std::shared_ptr<Aircraft>, Aircraft::ParseResult>())
        .def_readonly("ac", &Aircraft::SearchResult::ac)
        .def_readonly("parse_result", &Aircraft::SearchResult::parse_result);

    py::class_<Aircraft::Suggestion>(ac_class, "Suggestion")
        .def(py::init<std::shared_ptr<Aircraft>, double>())
        .def_readonly("ac", &Aircraft::Suggestion::ac)
        .def_readonly("score", &Aircraft::Suggestion::score);

    ac_class
        .def_static("search", &Aircraft::search, "s"_a)
        .def_static("suggest", &Aircraft::suggest, "s"_a);
    
    /*** PURCHASED AIRCRAFT ***/
    py::class_<PaxConfig> pc_class(m_ac, "PaxConfig");
    py::enum_<PaxConfig::Algorithm>(pc_class, "Algorithm")
        .value("FJY", PaxConfig::Algorithm::FJY).value("FYJ", PaxConfig::Algorithm::FYJ)
        .value("JFY", PaxConfig::Algorithm::JFY).value("JYF", PaxConfig::Algorithm::JYF)
        .value("YJF", PaxConfig::Algorithm::YJF).value("YFJ", PaxConfig::Algorithm::YFJ)
        .value("NONE", PaxConfig::Algorithm::NONE);
    pc_class
        .def_readonly("y", &PaxConfig::y)
        .def_readonly("j", &PaxConfig::j)
        .def_readonly("f", &PaxConfig::f)
        .def_readonly("valid", &PaxConfig::valid)
        .def_readonly("algorithm", &PaxConfig::algorithm);

    py::class_<CargoConfig> cc_class(m_ac, "CargoConfig");
    py::enum_<CargoConfig::Algorithm>(cc_class, "Algorithm")
        .value("L", CargoConfig::Algorithm::L).value("H", CargoConfig::Algorithm::H)
        .value("NONE", CargoConfig::Algorithm::NONE);
    cc_class
        .def_readonly("l", &CargoConfig::l)
        .def_readonly("h", &CargoConfig::h)
        .def_readonly("valid", &CargoConfig::valid)
        .def_readonly("algorithm", &CargoConfig::algorithm);

    py::class_<PurchasedAircraft, std::shared_ptr<PurchasedAircraft>, Aircraft> p_ac_class(m_ac, "PurchasedAircraft");
    py::class_<PurchasedAircraft::Config>(p_ac_class, "Config")
        .def_readonly("pax_config", &PurchasedAircraft::Config::pax_config)
        .def_readonly("cargo_config", &PurchasedAircraft::Config::cargo_config);
    p_ac_class
        .def_readonly("config", &PurchasedAircraft::config)
        .def("__repr__", &PurchasedAircraft::repr);


    /*** AIRPORT ***/
    py::class_<Airport, std::shared_ptr<Airport>> ap_class(m_ap, "Airport");
    ap_class
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
        .def("__repr__", &Airport::repr);

    py::enum_<Airport::SearchType>(ap_class, "SearchType")
        .value("ALL", Airport::SearchType::ALL)
        .value("IATA", Airport::SearchType::IATA)
        .value("ICAO", Airport::SearchType::ICAO)
        .value("NAME", Airport::SearchType::NAME)
        .value("ID", Airport::SearchType::ID);
    
    py::class_<Airport::ParseResult>(ap_class, "ParseResult")
        .def(py::init<Airport::SearchType, const std::string&>())
        .def_readonly("search_type", &Airport::ParseResult::search_type)
        .def_readonly("search_str", &Airport::ParseResult::search_str);

    py::class_<Airport::SearchResult>(ap_class, "SearchResult")
        .def(py::init<std::shared_ptr<Airport>, Airport::ParseResult>())
        .def_readonly("ap", &Airport::SearchResult::ap)
        .def_readonly("parse_result", &Airport::SearchResult::parse_result);

    py::class_<Airport::Suggestion>(ap_class, "Suggestion")
        .def(py::init<std::shared_ptr<Airport>, double>())
        .def_readonly("ap", &Airport::Suggestion::ap)
        .def_readonly("score", &Airport::Suggestion::score);

    // defined after nested classes
    ap_class
        .def_static("search", &Airport::search, "s"_a)
        .def_static("suggest", &Airport::suggest, "s"_a);

    /*** ROUTE ***/
    py::class_<Route>(m_route, "Route")
        .def_readonly("origin", &Route::origin)
        .def_readonly("destination", &Route::destination)
        .def_readonly("pax_demand", &Route::pax_demand)
        .def_readonly("cargo_demand", &Route::cargo_demand)
        .def_readonly("aircraft", &Route::aircraft)
        .def_readonly("ticket", &Route::ticket)
        .def_readonly("income", &Route::income)
        .def_readonly("direct_distance", &Route::direct_distance)
        .def_readonly("valid", &Route::valid)
        .def_static("from_airports", &Route::from_airports, "ap1"_a, "ap2"_a)
        .def_static("from_airports_with_aircraft", &Route::from_airports_with_aircraft, "ap1"_a, "ap2"_a, "ac"_a, "trips_per_day"_a = 1, "game_mode"_a = User::GameMode::EASY)
        .def("__repr__", &Route::repr);

    m.attr("__version__") = version;
}