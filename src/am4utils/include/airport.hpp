#pragma once
#include <string>

using std::string;

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

    void update_from_result(duckdb::unique_ptr<duckdb::QueryResult> result);

    static Airport _from_id(uint16_t id);
    static Airport _from_iata(string s);
    static Airport _from_icao(string s);

    static Airport from_auto(string s);

    string repr();
};

class AirportNotFoundException : public std::exception {
private:
    string searchtype;
    string searchstr;
    std::vector<Airport> suggestions;
public:
    AirportNotFoundException(string searchtype, string searchstr, std::vector<Airport> suggestions) : searchtype(searchtype), searchstr(searchstr), suggestions(suggestions) {}
    const char* what() const throw() { return ("Airport not found: " + searchtype + "='" + searchstr + "'").c_str(); }
    string get_searchtype() { return searchtype; }
    string get_searchstr() { return searchstr; }
    std::vector<Airport> get_suggestions() { return suggestions; }
};