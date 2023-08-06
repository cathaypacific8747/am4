#pragma once
#include <duckdb.hpp>
#include <string>
#include <vector>
#include <chrono>
#include "aircraft.hpp"

using TimePoint = std::chrono::time_point<std::chrono::system_clock>;

using std::string;

struct AllianceLog {
    struct Member {
        uint32_t id;
        string username; 
        TimePoint joined;
        uint32_t flights;
        uint32_t contributed;
        uint32_t daily_contribution;
        TimePoint online;
        float sv;
        uint32_t season;

        Member(uint32_t id, const string& username, const TimePoint& joined, uint32_t flights, uint32_t contributed, uint32_t daily_contribution, const TimePoint& online, float sv, uint32_t season);
    };

    string log_id;
    TimePoint log_time;
    uint32_t id;
    string name;
    uint32_t rank;
    uint8_t member_count;
    uint8_t max_members;
    double value;
    bool ipo;
    float min_sv;
    std::vector<Member> members;

    AllianceLog(uint32_t id, const string& name, uint32_t rank, uint8_t member_count, uint8_t max_members, double value, bool ipo, float min_sv, std::vector<Member> members);
    
    AllianceLog();
    AllianceLog(const duckdb::unique_ptr<duckdb::DataChunk>& chunk, idx_t row);
    AllianceLog& insert_to_db();

    static AllianceLog from_log_id(const string& log_id);
};

struct UserLog {
    struct Share {
        TimePoint ts; 
        float share;

        Share(const TimePoint& ts, float share);
    };

    struct Award {
        TimePoint ts;
        string award;

        Award(const TimePoint& ts, const string& award);
    };

    struct AircraftCount {
        string aircraft;
        int amount;
        Aircraft parsed_aircraft;

        AircraftCount(const string& aircraft, int amount);
    };

    struct RouteDetail {
        string origin;
        string stopover;
        string destination;
        int distance;
        TimePoint arrived;
    };

    uint32_t id;
    string log_id;
    TimePoint log_time;
    string username;
    uint16_t level;
    bool online;
    float share;
    uint32_t shares_available;
    uint32_t shares_sold;
    bool ipo;
    uint16_t fleet_count;
    uint16_t routes;
    string alliance;
    uint8_t achievements;
    bool game_mode; 
    uint32_t rank;
    uint8_t reputation;
    uint8_t cargo_reputation;
    TimePoint founded;
    string logo;

    std::vector<Share> share_log;
    std::vector<Award> awards;
    std::vector<UserLog::AircraftCount> fleet;
    std::vector<UserLog::RouteDetail> route_list;

    UserLog(
        uint32_t id, const string& username, uint16_t level, bool online, 
        float share, uint32_t shares_available, uint32_t shares_sold, bool ipo,
        uint16_t fleet_count, uint16_t routes, const string& alliance, 
        uint8_t achievements, bool game_mode, uint32_t rank, uint8_t reputation, uint8_t cargo_reputation,
        const TimePoint& founded, const string& logo,
        std::vector<Share> share_log, std::vector<Award> awards,
        std::vector<AircraftCount> fleet, std::vector<RouteDetail> route_list
    );
};