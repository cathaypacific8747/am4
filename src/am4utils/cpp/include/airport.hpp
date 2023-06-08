#pragma once
#include <string>
#include <sstream>
#include <duckdb.hpp>

#include "enums.h"

using std::string;
using std::vector;

struct Airport {
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
    bool valid = false;

    Airport();
    Airport(const duckdb::DataChunk& chunk, idx_t row);

    static Airport _from_id(uint16_t id);
    static Airport _from_iata(const string& s);
    static Airport _from_icao(const string& s);
    static Airport _from_name(const string& s);
    static Airport _from_all(const string& s);

    static std::vector<Airport> _suggest_iata(const string& s);
    static std::vector<Airport> _suggest_icao(const string& s);
    static std::vector<Airport> _suggest_name(const string& s);
    static std::vector<Airport> _suggest_all(const string& s);

    static Airport from_auto(string s);

    const string repr();
};

struct AirportSuggestion {
    Airport ap;
    double score;

    AirportSuggestion(const Airport& ap, double score) : ap(ap), score(score) {}
};

class AirportNotFoundException : public std::exception {
private:
    AirportSearchType searchtype;
    string searchstr;
    std::vector<Airport> suggestions;
public:
    AirportNotFoundException(AirportSearchType searchtype, string searchstr, std::vector<Airport> suggestions) : searchtype(searchtype), searchstr(searchstr), suggestions(suggestions) {}
    const char* what() const throw() {
        std::stringstream ss;
        string searchtype_str;
        switch (searchtype) {
            case AirportSearchType::ALL:
                searchtype_str = "all";
                break;
            case AirportSearchType::IATA:
                searchtype_str = "iata";
                break;
            case AirportSearchType::ICAO:
                searchtype_str = "icao";
                break;
            case AirportSearchType::NAME:
                searchtype_str = "name";
                break;
            case AirportSearchType::ID:
                searchtype_str = "id";
                break;
            default:
                searchtype_str = "(unknown)";
                break;
        }
        ss << "Airport not found - " << searchtype_str << ":" << searchstr;
        if (suggestions.size() > 0) {
            ss << ". Did you mean: ";
            for (auto ap : suggestions) {
                ss << "\n  " << ap.id << ": " << ap.iata << "/" << ap.icao << "/" << ap.name;
            }
        }
        return ss.str().c_str();
    }
    AirportSearchType get_searchtype() { return searchtype; }
    string get_searchstr() { return searchstr; }
    std::vector<Airport> get_suggestions() { return suggestions; }
};