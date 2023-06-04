#include <iostream>
#include <algorithm>
#include <string>
#include <duckdb.hpp>
#include "include/db.hpp"
#include "include/airport.hpp"
#include "include/route.hpp"

using std::string;
using namespace duckdb;

void Airport::update_from_result(duckdb::unique_ptr<duckdb::QueryResult> result) {
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return;

    id = chunk->GetValue(0, 0).GetValue<uint16_t>();
    name = chunk->GetValue(1, 0).GetValue<string>();
    fullname = chunk->GetValue(2, 0).GetValue<string>();
    country = chunk->GetValue(3, 0).GetValue<string>();
    continent = chunk->GetValue(4, 0).GetValue<string>();
    iata = chunk->GetValue(5, 0).GetValue<string>();
    icao = chunk->GetValue(6, 0).GetValue<string>();
    lat = chunk->GetValue(7, 0).GetValue<double>();
    lng = chunk->GetValue(8, 0).GetValue<double>();
    rwy = chunk->GetValue(9, 0).GetValue<uint16_t>();
    market = chunk->GetValue(10, 0).GetValue<uint8_t>();
    hub_cost = chunk->GetValue(11, 0).GetValue<uint32_t>();
    rwy_codes = chunk->GetValue(12, 0).GetValue<string>();
    valid = true;
}

string Airport::repr() {
    return "<Airport id=" + std::to_string(id) + " name='" + name + "' fullname='" + fullname + "' country='" + country + "' continent='" + continent + "' iata='" + iata + "' icao='" + icao + "' lat=" + std::to_string(lat) + " lng=" + std::to_string(lng) + " rwy=" + std::to_string(rwy) + " market=" + std::to_string(market) + " hub_cost=" + std::to_string(hub_cost) + " rwy_codes='" + rwy_codes + "'>";
}

Airport Airport::_from_id(uint16_t id) {
    Airport ap;
    auto result = Database::Client()->get_airport_by_id->Execute(id);
    CHECK_SUCCESS(result);

    ap.update_from_result(std::move(result));

    return ap;
}

Airport Airport::_from_iata(string s) {
    Airport ap;
    auto result = Database::Client()->get_airport_by_iata->Execute(s);
    CHECK_SUCCESS(result);
    
    ap.update_from_result(std::move(result));
    return ap;
}

Airport Airport::_from_icao(string s) {
    Airport ap;
    auto result = Database::Client()->get_airport_by_icao->Execute(s);
    CHECK_SUCCESS(result);

    ap.update_from_result(std::move(result));
    return ap;
}

Airport Airport::from_auto(string s) {
    Airport ap;
    if (s.empty()) return ap;
    if (s.size() == 3) {
        ap = Airport::_from_iata(s);
        if (ap.valid) return ap;
        throw AirportNotFoundException("iata", s, {});
    } else if (s.size() == 4) {
        ap = Airport::_from_icao(s);
        if (ap.valid) return ap;
        throw AirportNotFoundException("icao", s, {});
    }
    return ap;
}