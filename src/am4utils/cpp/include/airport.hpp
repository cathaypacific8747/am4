#pragma once
#include <string>
#include <sstream>
#include <memory>
#include <duckdb.hpp>

using std::string;
using std::to_string;
using std::shared_ptr;
using std::make_shared;

struct Airport {
    enum class SearchType {
        ALL,
        IATA,
        ICAO,
        NAME,
        ID,
    };

    uint16_t id;
    string name;
    string fullname;
    string country;
    string continent;
    string iata;
    string icao;
    double lat;
    double lng;
    uint16_t rwy;
    uint8_t market;
    uint32_t hub_cost;
    string rwy_codes;
    bool valid;

    struct ParseResult {
        Airport::SearchType search_type;
        string search_str;

        ParseResult(Airport::SearchType search_type, const string& search_str) : search_type(search_type), search_str(search_str) {}
    };
    
    struct SearchResult {
        shared_ptr<Airport> ap;
        Airport::ParseResult parse_result;

        SearchResult(shared_ptr<Airport> ap, Airport::ParseResult parse_result) : ap(ap), parse_result(parse_result) {}
    };

    struct Suggestion {
        shared_ptr<Airport> ap;
        double score;

        Suggestion() : ap(make_shared<Airport>()), score(0) {}
        Suggestion(shared_ptr<Airport> ap, double score) : ap(ap), score(score) {}
    };

    Airport();
    static ParseResult parse(const string& s);
    static SearchResult search(const string& s);
    static std::vector<Airport::Suggestion> suggest(const ParseResult& parse_result);

    Airport(const duckdb::unique_ptr<duckdb::DataChunk>& chunk, idx_t row);
    static const string repr(const Airport& ap);
};

inline const string to_string(Airport::SearchType st);

#if BUILD_PYBIND == 1
#include "binder.hpp"

py::dict to_dict(const Airport& ap);
#endif