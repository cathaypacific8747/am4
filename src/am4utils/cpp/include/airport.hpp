#pragma once
#include <string>
#include <sstream>
#include <duckdb.hpp>

using std::string;
using std::to_string;
using std::vector;

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
    bool valid = false;

    Airport();
    static Airport from_str(string s);

    Airport(const duckdb::DataChunk& chunk, idx_t row);
    static Airport from_id(uint16_t id);
    static Airport from_iata(const string& s);
    static Airport from_icao(const string& s);
    static Airport from_name(const string& s);
    static Airport from_all(const string& s);
    static std::vector<Airport> suggest_iata(const string& s);
    static std::vector<Airport> suggest_icao(const string& s);
    static std::vector<Airport> suggest_name(const string& s);
    static std::vector<Airport> suggest_all(const string& s);
    static const string repr(const Airport& ap);
};

inline const string to_string(Airport::SearchType st);

struct AirportSuggestion {
    Airport ap;
    double score;

    AirportSuggestion(const Airport& ap, double score) : ap(ap), score(score) {}
};

class AirportNotFoundException : public std::exception {
private:
    Airport::SearchType searchtype;
    string searchstr;
    std::vector<Airport> suggestions;
public:
    AirportNotFoundException(Airport::SearchType searchtype, string searchstr, std::vector<Airport> suggestions) : searchtype(searchtype), searchstr(searchstr), suggestions(suggestions) {}
    const char* what() const throw() {
        std::stringstream ss;
        string searchtype_str = to_string(searchtype);
        ss << "Airport not found - " << searchtype_str << ":" << searchstr;
        if (suggestions.size() > 0) {
            ss << ". Did you mean: ";
            for (auto ap : suggestions) {
                ss << "\n  " << ap.id << ": " << ap.iata << "/" << ap.icao << "/" << ap.name;
            }
        }
        return ss.str().c_str();
    }
    Airport::SearchType get_searchtype() { return searchtype; }
    string get_searchstr() { return searchstr; }
    std::vector<Airport> get_suggestions() { return suggestions; }
};