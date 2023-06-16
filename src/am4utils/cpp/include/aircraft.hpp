#pragma once
#include <string>
#include <cstdint>
#include <iomanip>
#include <duckdb.hpp>

#include "user.hpp"
#include "ticket.hpp"
#include "demand.hpp"

using std::string;

struct Aircraft {
    enum class Type {
        PAX = 0,
        CARGO = 1,
        VIP = 2
    };

    enum class SearchType {
        ALL = 0,
        ID = 1,
        SHORTNAME = 2,
        NAME = 3
    };

    uint16_t id;
    string shortname;
    string manufacturer;
    string name;
    Type type;
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
    Aircraft::SearchType searchtype;
    string searchstr;
    std::vector<Aircraft> suggestions;
public:
    AircraftNotFoundException(Aircraft::SearchType searchtype, string searchstr, std::vector<Aircraft> suggestions) : searchtype(searchtype), searchstr(searchstr), suggestions(suggestions) {}
    const char* what() const throw() {
        std::stringstream ss;
        string searchtype_str;
        switch (searchtype) {
            case Aircraft::SearchType::ALL:
                searchtype_str = "all";
                break;
            case Aircraft::SearchType::ID:
                searchtype_str = "id";
                break;
            case Aircraft::SearchType::SHORTNAME:
                searchtype_str = "shortname";
                break;
            case Aircraft::SearchType::NAME:
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
    Aircraft::SearchType get_searchtype() { return searchtype; }
    string get_searchstr() { return searchstr; }
    std::vector<Aircraft> get_suggestions() { return suggestions; }
};

struct PaxConfig {
    enum class Algorithm {
        FJY, FYJ,
        JFY, JYF,
        YJF, YFJ,
        NONE
    };

    uint16_t y = 0;
    uint16_t j = 0;
    uint16_t f = 0;
    bool valid = false;
    Algorithm algorithm;

    static inline PaxConfig calc_fjy_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_fyj_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_jfy_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_jyf_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_yfj_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);
    static inline PaxConfig calc_yjf_conf(const PaxDemand& d_pf, uint16_t capacity, float distance);

    static PaxConfig calc_pax_conf(const PaxDemand& pax_demand, uint16_t capacity, float distance, uint16_t trips_per_day = 1, User::GameMode game_mode = User::GameMode::EASY);
};

struct CargoConfig { // percent
    enum class Algorithm {
        L, H,
        NONE
    };

    uint8_t l = 0;
    uint8_t h = 0;
    bool valid = false;
    Algorithm algorithm;

    static inline CargoConfig calc_l_conf(const CargoDemand& d_pf, uint32_t capacity);
    static inline CargoConfig calc_h_conf(const CargoDemand& d_pf, uint32_t capacity);

    static CargoConfig calc_cargo_conf(const CargoDemand& cargo_demand, uint32_t capacity, uint16_t trips_per_day = 1, uint8_t l_training = 0);
};

struct PurchasedAircraft : Aircraft {
    union Config {
        PaxConfig pax_config;
        CargoConfig cargo_config;

        Config() {}
        Config(const PaxConfig& pax_config) : pax_config(pax_config) {}
        Config(const CargoConfig& cargo_config) : cargo_config(cargo_config) {}
    };
    Config config;
    // bool has_speed_mod = false;
    // bool has_co2_mod = false;

    PurchasedAircraft() {}
    PurchasedAircraft(const Aircraft& ac, const PaxConfig& pax_config) : Aircraft(ac), config(pax_config) {}
    PurchasedAircraft(const Aircraft& ac, const CargoConfig& cargo_config) : Aircraft(ac), config(cargo_config) {}
};