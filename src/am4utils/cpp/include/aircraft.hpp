#pragma once
#include <string>
#include <cstdint>
#include <duckdb.hpp>
#include <iomanip>

#include "enums.h"

using std::string;

struct Aircraft {
    uint16_t id;
    string shortname;
    string manufacturer;
    string name;
    AircraftType type;
    uint8_t priority;
    uint16_t eid;
    string ename;
    float speed;
    float fuel;
    float co2;
    uint32_t cost;
    uint32_t capacity;
    uint16_t rwy;
    uint32_t check_cost;
    uint16_t range;
    uint16_t ceil;
    uint16_t maint;
    uint8_t pilots;
    uint8_t crew;
    uint8_t engineers;
    uint8_t technicians;
    string img;
    uint8_t wingspan;
    uint8_t length;

    bool valid = false;

    Aircraft();
    Aircraft(const duckdb::DataChunk& chunk, idx_t row);

    static Aircraft _from_id(uint16_t id, uint8_t priority = 0);
    static Aircraft _from_shortname(const string& s, uint8_t priority = 0);
    static Aircraft _from_name(const string& s, uint8_t priority = 0);
    static Aircraft _from_all(const string& s, uint8_t priority = 0);

    static std::vector<Aircraft> _suggest_shortname(const string& s, uint8_t priority = 0);
    static std::vector<Aircraft> _suggest_name(const string& s, uint8_t priority = 0);
    static std::vector<Aircraft> _suggest_all(const string& s, uint8_t priority = 0);

    static Aircraft from_auto(string s);

    const string repr();
};

struct AircraftSuggestion {
    Aircraft ac;
    double score;

    AircraftSuggestion(const Aircraft& ac, double score) : ac(ac), score(score) {}
};

class AircraftNotFoundException : public std::exception {
private:
    AircraftSearchType searchtype;
    string searchstr;
    std::vector<Aircraft> suggestions;
public:
    AircraftNotFoundException(AircraftSearchType searchtype, string searchstr, std::vector<Aircraft> suggestions) : searchtype(searchtype), searchstr(searchstr), suggestions(suggestions) {}
    const char* what() const throw() {
        std::stringstream ss;
        string searchtype_str;
        switch (searchtype) {
            case AircraftSearchType::ALL:
                searchtype_str = "all";
                break;
            case AircraftSearchType::ID:
                searchtype_str = "id";
                break;
            case AircraftSearchType::SHORTNAME:
                searchtype_str = "shortname";
                break;
            case AircraftSearchType::NAME:
                searchtype_str = "name";
                break;
            default:
                searchtype_str = "(unknown)";
                break;
        }
        ss << "Aircraft not found - " << searchtype_str << ":" << searchstr;
        if (suggestions.size() > 0) {
            ss << ". Did you mean: ";
            for (auto ac : suggestions) {
                ss << "\n  " << std::setw(3) << ac.id << ": " << ac.shortname << "/" << ac.name;
            }
        }
        return ss.str().c_str();
    }
    AircraftSearchType get_searchtype() { return searchtype; }
    string get_searchstr() { return searchstr; }
    std::vector<Aircraft> get_suggestions() { return suggestions; }
};