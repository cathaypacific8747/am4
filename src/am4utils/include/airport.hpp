#include <string>

using namespace std;

class Airport {
public:
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

    static Airport from_id(int id);
};