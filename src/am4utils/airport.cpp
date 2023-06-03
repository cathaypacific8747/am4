#include <iostream>
#include <duckdb.hpp>
#include "include/db.hpp"
#include "include/airport.hpp"
#include "include/route.hpp"

using namespace std;
using namespace duckdb;

Airport Airport::from_id(int id) {
    Airport ap;

    auto result = Database::Client()->get_airport_by_id->Execute(id);
    CHECK_SUCCESS(result);
    
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return ap;

    // pretty dumb: maybe there's a better way to do this???
    ap.id = chunk->GetValue(0, 0).GetValue<uint16_t>();
    ap.name = chunk->GetValue(1, 0).GetValue<string>();
    ap.fullname = chunk->GetValue(2, 0).GetValue<string>();
    ap.country = chunk->GetValue(3, 0).GetValue<string>();
    ap.continent = chunk->GetValue(4, 0).GetValue<string>();
    ap.iata = chunk->GetValue(5, 0).GetValue<string>();
    ap.icao = chunk->GetValue(6, 0).GetValue<string>();
    ap.lat = chunk->GetValue(7, 0).GetValue<double>();
    ap.lng = chunk->GetValue(8, 0).GetValue<double>();
    ap.rwy = chunk->GetValue(9, 0).GetValue<uint16_t>();
    ap.market = chunk->GetValue(10, 0).GetValue<uint8_t>();
    ap.hub_cost = chunk->GetValue(11, 0).GetValue<uint32_t>();
    ap.rwy_codes = chunk->GetValue(12, 0).GetValue<string>();
    ap.valid = true;

    return ap;
}