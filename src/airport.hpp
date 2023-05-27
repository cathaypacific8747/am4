#include <string>

struct Airport {
    int id;
    std::string name;
    std::string fullname;
    std::string country;
    std::string continent;
    std::string iata;
    std::string icao;
    float lat;
    float lng;
    int rwy;
    int market;
    int hub_cost;
    std::string rwy_codes;
};

int get_airport_by_id(int id);