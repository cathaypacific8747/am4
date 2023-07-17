#include <iostream>
#include <algorithm>
#include <string>

#include "include/db.hpp"
#include "include/airport.hpp"
#include "include/route.hpp"

Airport::Airport() : valid(false) {}

Airport::ParseResult Airport::parse(const string& s) {
    string s_upper = s;
    std::transform(s_upper.begin(), s_upper.end(), s_upper.begin(), ::toupper);

    if (s_upper.substr(0, 5) == "IATA:") {
        return Airport::ParseResult(Airport::SearchType::IATA, s_upper.substr(5));
    } else if (s_upper.substr(0, 5) == "ICAO:") {
        return Airport::ParseResult(Airport::SearchType::ICAO, s_upper.substr(5));
    } else if (s_upper.substr(0, 5) == "NAME:") {
        return Airport::ParseResult(Airport::SearchType::NAME, s_upper.substr(5));
    } else if (s_upper.substr(0, 3) == "ID:") {
        try {
            std::ignore = std::stoi(s.substr(3));
            return Airport::ParseResult(Airport::SearchType::ID, s.substr(3));
        } catch (const std::invalid_argument&) {
        } catch (const std::out_of_range&) {
        }
    } else if (s_upper.substr(0, 4) == "ALL:") {
        return Airport::ParseResult(Airport::SearchType::ALL, s_upper.substr(4));
    }
    return Airport::ParseResult(Airport::SearchType::ALL, s_upper);
}

Airport::SearchResult Airport::search(const string& s) {
    auto parse_result = Airport::parse(s);
    Airport ap;
    switch (parse_result.search_type) {
        case Airport::SearchType::ALL:
            ap = Database::Client()->get_airport_by_all(parse_result.search_str);
            break;
        case Airport::SearchType::IATA:
            ap = Database::Client()->get_airport_by_iata(parse_result.search_str);
            break;
        case Airport::SearchType::ICAO:
            ap = Database::Client()->get_airport_by_icao(parse_result.search_str);
            break;
        case Airport::SearchType::NAME:
            ap = Database::Client()->get_airport_by_name(parse_result.search_str);
            break;
        case Airport::SearchType::ID:
            ap = Database::Client()->get_airport_by_id(std::stoi(parse_result.search_str));
            break;
    }
    return Airport::SearchResult(make_shared<Airport>(ap), parse_result);
}

// note: searchtype id will return no suggestions.
std::vector<Airport::Suggestion> Airport::suggest(const Airport::ParseResult& parse_result) {
    std::vector<Airport::Suggestion> suggestions;
    switch (parse_result.search_type) {
        case Airport::SearchType::ALL:
            suggestions = Database::Client()->suggest_airport_by_all(parse_result.search_str);
            break;
        case Airport::SearchType::IATA:
            suggestions = Database::Client()->suggest_airport_by_iata(parse_result.search_str);
            break;
        case Airport::SearchType::ICAO:
            suggestions = Database::Client()->suggest_airport_by_icao(parse_result.search_str);
            break;
        case Airport::SearchType::NAME:
            suggestions = Database::Client()->suggest_airport_by_name(parse_result.search_str);
            break;
        default:
            return suggestions;
    }
    return suggestions;
}


Airport::Airport(const duckdb::unique_ptr<duckdb::DataChunk>& chunk, idx_t row) :
    id(chunk->GetValue(0, row).GetValue<uint16_t>()),
    name(chunk->GetValue(1, row).GetValue<string>()),
    fullname(chunk->GetValue(2, row).GetValue<string>()),
    country(chunk->GetValue(3, row).GetValue<string>()),
    continent(chunk->GetValue(4, row).GetValue<string>()),
    iata(chunk->GetValue(5, row).GetValue<string>()),
    icao(chunk->GetValue(6, row).GetValue<string>()),
    lat(chunk->GetValue(7, row).GetValue<double>()),
    lng(chunk->GetValue(8, row).GetValue<double>()),
    rwy(chunk->GetValue(9, row).GetValue<uint16_t>()),
    market(chunk->GetValue(10, row).GetValue<uint8_t>()),
    hub_cost(chunk->GetValue(11, row).GetValue<uint32_t>()),
    rwy_codes(chunk->GetValue(12, row).GetValue<string>()),
    valid(true) {}

const string to_string(Airport::SearchType st) {
    switch (st) {
        case Airport::SearchType::ALL:
            return "ALL";
        case Airport::SearchType::IATA:
            return "IATA";
        case Airport::SearchType::ICAO:
            return "ICAO";
        case Airport::SearchType::NAME:
            return "NAME";
        case Airport::SearchType::ID:
            return "ID";
        default:
            return "[UNKNOWN]";
    }
}

const string Airport::repr(const Airport& ap) {
    if (!ap.valid) return "<Airport.INVALID>";
    return "<Airport." + to_string(ap.id) + " " + ap.iata + "|" + ap.icao + "|" + ap.name + "," +
    ap.country + " @ " + to_string(ap.lat) + "," + to_string(ap.lng) + " " +
    to_string(ap.rwy) + "ft " + to_string(ap.market) + "% $" + to_string(ap.hub_cost) + ">";
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict to_dict(const Airport& ap) {
    return py::dict(
        "id"_a=ap.id,
        "name"_a=ap.name,
        "fullname"_a=ap.fullname,
        "country"_a=ap.country,
        "continent"_a=ap.continent,
        "iata"_a=ap.iata,
        "icao"_a=ap.icao,
        "lat"_a=ap.lat,
        "lng"_a=ap.lng,
        "rwy"_a=ap.rwy,
        "market"_a=ap.market,
        "hub_cost"_a=ap.hub_cost,
        "rwy_codes"_a=ap.rwy_codes
    );
}

void pybind_init_airport(py::module_& m) {
    py::module_ m_ap = m.def_submodule("airport");
    
    py::class_<Airport, shared_ptr<Airport>> ap_class(m_ap, "Airport");
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
        .def("__repr__", &Airport::repr)
        .def("to_dict", py::overload_cast<const Airport&>(&to_dict));
    
    py::enum_<Airport::SearchType>(ap_class, "SearchType")
        .value("ALL", Airport::SearchType::ALL)
        .value("IATA", Airport::SearchType::IATA)
        .value("ICAO", Airport::SearchType::ICAO)
        .value("NAME", Airport::SearchType::NAME)
        .value("ID", Airport::SearchType::ID);
    
    py::class_<Airport::ParseResult>(ap_class, "ParseResult")
        .def(py::init<Airport::SearchType, const string&>())
        .def_readonly("search_type", &Airport::ParseResult::search_type)
        .def_readonly("search_str", &Airport::ParseResult::search_str);

    py::class_<Airport::SearchResult>(ap_class, "SearchResult")
        .def(py::init<shared_ptr<Airport>, Airport::ParseResult>())
        .def_readonly("ap", &Airport::SearchResult::ap)
        .def_readonly("parse_result", &Airport::SearchResult::parse_result);

    py::class_<Airport::Suggestion>(ap_class, "Suggestion")
        .def(py::init<shared_ptr<Airport>, double>())
        .def_readonly("ap", &Airport::Suggestion::ap)
        .def_readonly("score", &Airport::Suggestion::score);

    ap_class
        .def_static("search", &Airport::search, "s"_a)
        .def_static("suggest", &Airport::suggest, "s"_a);
}
#endif