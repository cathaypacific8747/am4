#include <iostream>
#include <algorithm>
#include <string>

#include "include/airport.hpp"
#include "include/route.hpp"
#include "include/db.hpp"

using std::string;
using namespace duckdb;

Airport::Airport() : valid(false) {}

Airport Airport::from_str(string s) {
    Airport ap;
    Airport::SearchType search_type = Airport::SearchType::ALL;

    string s_upper = s;
    std::transform(s_upper.begin(), s_upper.end(), s_upper.begin(), ::toupper);

    // search airports
    if (s_upper.substr(0, 5) == "IATA:") {
        search_type = Airport::SearchType::IATA;
        s = s_upper.substr(5);
        ap = Airport::from_iata(s);
    } else if (s_upper.substr(0, 5) == "ICAO:") {
        search_type = Airport::SearchType::ICAO;
        s = s_upper.substr(5);
        ap = Airport::from_icao(s);
    } else if (s_upper.substr(0, 5) == "NAME:") {
        search_type = Airport::SearchType::NAME;
        s = s_upper.substr(5);
        ap = Airport::from_name(s);
    } else if (s_upper.substr(0, 3) == "ID:") {
        search_type = Airport::SearchType::ID;
        s = s.substr(3);
        try {
            ap = Airport::from_id(std::stoi(s));
        } catch (std::invalid_argument& e) {
        } catch (std::out_of_range& e) { // silently skipping, empty suggestions will be thrown later on
        }
    } else if (s_upper.substr(0, 4) == "ALL:") {
        s = s_upper.substr(4);
        ap = Airport::from_all(s);
    } else {
        s = s_upper;
        ap = Airport::from_all(s);
    }

    if (ap.valid) return ap;
    
    // empty airports, suggest and throw error
    std::vector<Airport> airports;
    switch (search_type) {
        case Airport::SearchType::ALL:
            airports = Airport::suggest_all(s);
            break;
        case Airport::SearchType::IATA:
            airports = Airport::suggest_iata(s);
            break;
        case Airport::SearchType::ICAO:
            airports = Airport::suggest_icao(s);
            break;
        case Airport::SearchType::NAME:
            airports = Airport::suggest_name(s);
            break;
    }

    throw AirportNotFoundException(search_type, s, airports);
}


Airport::Airport(const duckdb::DataChunk& chunk, idx_t row) :
    id(chunk.GetValue(0, row).GetValue<uint16_t>()),
    name(chunk.GetValue(1, row).GetValue<string>()),
    fullname(chunk.GetValue(2, row).GetValue<string>()),
    country(chunk.GetValue(3, row).GetValue<string>()),
    continent(chunk.GetValue(4, row).GetValue<string>()),
    iata(chunk.GetValue(5, row).GetValue<string>()),
    icao(chunk.GetValue(6, row).GetValue<string>()),
    lat(chunk.GetValue(7, row).GetValue<double>()),
    lng(chunk.GetValue(8, row).GetValue<double>()),
    rwy(chunk.GetValue(9, row).GetValue<uint16_t>()),
    market(chunk.GetValue(10, row).GetValue<uint8_t>()),
    hub_cost(chunk.GetValue(11, row).GetValue<uint32_t>()),
    rwy_codes(chunk.GetValue(12, row).GetValue<string>()),
    valid(true) {}

Airport Airport::from_id(uint16_t id) {
    auto result = Database::Client()->get_airport_by_id->Execute(id);
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}

Airport Airport::from_iata(const string& s) {
    auto result = Database::Client()->get_airport_by_iata->Execute(s.c_str()); // note: std::string somehow converts to BLOB
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}

Airport Airport::from_icao(const string& s) {
    auto result = Database::Client()->get_airport_by_icao->Execute(s.c_str());
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}

Airport Airport::from_name(const string& s) {
    auto result = Database::Client()->get_airport_by_name->Execute(s.c_str());
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}

Airport Airport::from_all(const string& s) {
    auto result = Database::Client()->get_airport_by_all->Execute(s.c_str());
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}


std::vector<Airport> Airport::suggest_iata(const string& s) {
    std::vector<Airport> airports;
    auto result = Database::Client()->suggest_airport_by_iata->Execute(s.c_str());
    CHECK_SUCCESS(result);
    while (auto chunk = result->Fetch()) {
        for (idx_t i = 0; i < chunk->size(); i++) {
            airports.emplace_back(*chunk, i);
        }
    }
    return airports;
}

std::vector<Airport> Airport::suggest_icao(const string& s) {
    std::vector<Airport> airports;
    auto result = Database::Client()->suggest_airport_by_icao->Execute(s.c_str());
    CHECK_SUCCESS(result);
    while (auto chunk = result->Fetch()) {
        for (idx_t i = 0; i < chunk->size(); i++) {
            airports.emplace_back(*chunk, i);
        }
    }
    return airports;
}

std::vector<Airport> Airport::suggest_name(const string& s) {
    std::vector<Airport> airports;
    auto result = Database::Client()->suggest_airport_by_name->Execute(s.c_str());
    CHECK_SUCCESS(result);
    while (auto chunk = result->Fetch()) {
        for (idx_t i = 0; i < chunk->size(); i++) {
            airports.emplace_back(*chunk, i);
        }
    }
    return airports;
}

// TODO: remove duplicates
std::vector<Airport> Airport::suggest_all(const string& s) {
    std::vector<Airport> airports;
    std::vector<AirportSuggestion> suggestions;
    for (auto& stmt : {
        Database::Client()->suggest_airport_by_iata.get(),
        Database::Client()->suggest_airport_by_icao.get(),
        Database::Client()->suggest_airport_by_name.get(),
    }) {
        auto result = stmt->Execute(s.c_str());
        CHECK_SUCCESS(result);
        auto chunk = result->Fetch();
        if (!chunk || chunk->size() == 0) continue;

        for (idx_t i = 0; i < chunk->size(); i++) {
            suggestions.emplace_back(
                Airport(*chunk, i),
                chunk->GetValue(13, i).GetValue<double>()
            );
        }
    }

    std::partial_sort(suggestions.begin(), suggestions.begin() + 5, suggestions.end(), [](const AirportSuggestion& a, const AirportSuggestion& b) {
        return a.score > b.score;
    });

    for (size_t i = 0; i < std::min<size_t>(5, suggestions.size()); i++) {
        airports.push_back(std::move(suggestions[i].ap));
    }

    return airports;
}

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
    return "<Airport." + to_string(ap.id) + " " + ap.iata + "|" + ap.icao + "|" + ap.name + "," +
    ap.country + " @ " + to_string(ap.lat) + "," + to_string(ap.lng) + " " +
    to_string(ap.rwy) + "ft " + to_string(ap.market) + "% $" + to_string(ap.hub_cost) + ">";
}