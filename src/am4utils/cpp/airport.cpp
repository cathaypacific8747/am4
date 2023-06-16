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
            uint16_t _ = std::stoi(s.substr(3));
            return Airport::ParseResult(Airport::SearchType::ID, s.substr(3));
        } catch (std::invalid_argument& e) {
        } catch (std::out_of_range& e) {
        }
    } else if (s_upper.substr(0, 4) == "ALL:") {
        return Airport::ParseResult(Airport::SearchType::ALL, s_upper.substr(4));
    }
    return Airport::ParseResult(Airport::SearchType::ALL, s_upper);
}

Airport::SearchResult Airport::search(const string& s) {
    auto parse_result = Airport::ParseResult(Airport::parse(s));
    duckdb::unique_ptr<duckdb::QueryResult> result;
    switch (parse_result.search_type) {
        case Airport::SearchType::ALL:
            result = Database::Client()->get_airport_by_all->Execute(parse_result.search_str.c_str());
            break;
        case Airport::SearchType::IATA:
            result = Database::Client()->get_airport_by_iata->Execute(parse_result.search_str.c_str());
            break;
        case Airport::SearchType::ICAO:
            result = Database::Client()->get_airport_by_icao->Execute(parse_result.search_str.c_str());
            break;
        case Airport::SearchType::NAME:
            result = Database::Client()->get_airport_by_name->Execute(parse_result.search_str.c_str());
            break;
        case Airport::SearchType::ID:
            result = Database::Client()->get_airport_by_id->Execute(std::stoi(parse_result.search_str));
            break;
    }
    CHECK_SUCCESS(result);
    duckdb::unique_ptr<duckdb::DataChunk> chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport::SearchResult(make_shared<Airport>(), parse_result);

    return Airport::SearchResult(make_shared<Airport>(chunk, 0), parse_result);
}

// note: searchtype id will return no suggestions.
std::vector<Airport::Suggestion> Airport::suggest(const Airport::ParseResult& parse_result) {
    std::vector<Airport::Suggestion> suggestions;
    if (parse_result.search_type == Airport::SearchType::ALL) {
        for (auto& stmt : {
            Database::Client()->suggest_airport_by_iata.get(),
            Database::Client()->suggest_airport_by_icao.get(),
            Database::Client()->suggest_airport_by_name.get(),
        }) {
            auto result = stmt->Execute(parse_result.search_str.c_str());
            CHECK_SUCCESS(result);
            auto chunk = result->Fetch();
            if (!chunk || chunk->size() == 0) continue;

            for (idx_t i = 0; i < chunk->size(); i++) {
                // TODO: ensure no duplicates
                suggestions.emplace_back(
                    make_shared<Airport>(chunk, i),
                    chunk->GetValue(13, i).GetValue<double>()
                );
            }
        }
        std::partial_sort(suggestions.begin(), suggestions.begin() + 5, suggestions.end(), [](const Airport::Suggestion& a, const Airport::Suggestion& b) {
            return a.score > b.score;
        });
        suggestions.resize(5);
    } else {
        duckdb::unique_ptr<duckdb::QueryResult> result;
        switch (parse_result.search_type) {
            case Airport::SearchType::IATA:
                result = Database::Client()->suggest_airport_by_iata->Execute(parse_result.search_str.c_str());
                break;
            case Airport::SearchType::ICAO:
                result = Database::Client()->suggest_airport_by_icao->Execute(parse_result.search_str.c_str());
                break;
            case Airport::SearchType::NAME:
                result = Database::Client()->suggest_airport_by_name->Execute(parse_result.search_str.c_str());
                break;
        }
        CHECK_SUCCESS(result);
        while (auto chunk = result->Fetch()) {
            for (idx_t i = 0; i < chunk->size(); i++) {
                suggestions.emplace_back(
                    make_shared<Airport>(chunk, i),
                    chunk->GetValue(13, i).GetValue<double>()
                );
            }
        }
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
    return "<Airport." + to_string(ap.id) + " " + ap.iata + "|" + ap.icao + "|" + ap.name + "," +
    ap.country + " @ " + to_string(ap.lat) + "," + to_string(ap.lng) + " " +
    to_string(ap.rwy) + "ft " + to_string(ap.market) + "% $" + to_string(ap.hub_cost) + ">";
}