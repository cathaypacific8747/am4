#include "include/log.hpp"
#include "include/db.hpp"

// aircraft log - class should first be constructed via pydantic model dumping then (optionally) inserted to the db.
TimePoint to_timepoint(const duckdb::timestamp_t& timestamp) {
    using namespace std::chrono;
    return time_point<system_clock>(duration_cast<system_clock::duration>(microseconds(int64_t(timestamp))));
}

duckdb::timestamp_t to_ddb_timestamp(const TimePoint& timepoint) {
    using namespace std::chrono;
    return duckdb::Timestamp::FromEpochMicroSeconds(duration_cast<microseconds>(timepoint.time_since_epoch()).count());
}

AllianceLog::Member::Member(uint32_t id, const string& username, const TimePoint& joined, uint32_t flights, uint32_t contributed, uint32_t daily_contribution, const TimePoint& online, float sv, uint32_t season) :
    id(id),
    username(username),
    joined(joined),
    flights(flights),
    contributed(contributed),
    daily_contribution(daily_contribution),
    online(online),
    sv(sv),
    season(season)
{}

AllianceLog::AllianceLog(uint32_t id, const string& name, uint32_t rank, uint8_t member_count, uint8_t max_members, double value, bool ipo, float min_sv, std::vector<AllianceLog::Member> members) :
    log_id("00000000-0000-0000-0000-000000000000"),
    log_time(TimePoint(std::chrono::seconds(0))),
    id(id),
    name(name),
    rank(rank),
    member_count(member_count),
    max_members(max_members),
    value(value),
    ipo(ipo),
    min_sv(min_sv),
    members(members)
{}

const duckdb::LogicalType m_struct_types = duckdb::LogicalType::STRUCT(duckdb::child_list_t<duckdb::LogicalType>({
    {"id", duckdb::LogicalType::UINTEGER},
    {"username", duckdb::LogicalType::VARCHAR},
    {"joined", duckdb::LogicalType::TIMESTAMP},
    {"flights", duckdb::LogicalType::UINTEGER},
    {"contributed", duckdb::LogicalType::UINTEGER},
    {"daily_contribution", duckdb::LogicalType::UINTEGER},
    {"online", duckdb::LogicalType::TIMESTAMP},
    {"sv", duckdb::LogicalType::FLOAT},
    {"season", duckdb::LogicalType::UINTEGER}
}));
AllianceLog& AllianceLog::insert_to_db() {
    duckdb::Value log_id = duckdb::Value::UUID(duckdb::UUID::GenerateRandomUUID());
    duckdb::timestamp_t log_time = duckdb::Timestamp::GetCurrentTimestamp(); // microseconds
    const auto& connection = Database::Client()->connection;

    duckdb::Value m_value;
    if (this->members.empty())
        m_value = duckdb::Value::EMPTYLIST(m_struct_types);
    else {
        duckdb::vector<duckdb::Value> members;
        members.reserve(this->members.size());
        for (const auto& m : this->members) {
            members.push_back(duckdb::Value::STRUCT(duckdb::child_list_t<duckdb::Value>({
                {"id", duckdb::Value::UINTEGER(m.id)},
                {"username", duckdb::Value(m.username)},
                {"joined", duckdb::Value::TIMESTAMP(to_ddb_timestamp(m.joined))},
                {"flights", duckdb::Value::UINTEGER(m.flights)},
                {"contributed", duckdb::Value::UINTEGER(m.contributed)},
                {"daily_contribution", duckdb::Value::UINTEGER(m.daily_contribution)},
                {"online", duckdb::Value::TIMESTAMP(to_ddb_timestamp(m.online))},
                {"sv", duckdb::Value::FLOAT(m.sv)},
                {"season", duckdb::Value::UINTEGER(m.season)}
            })));
        }
        m_value = duckdb::Value::LIST(m_struct_types, members);
    }

    connection->BeginTransaction();
    duckdb::Appender main_appender(*connection, "alliance_log");
    main_appender.AppendRow(
        log_id, log_time,
        this->id, this->name.c_str(),
        this->rank, this->member_count, this->max_members,
        this->value, this->ipo, this->min_sv,
        m_value
    );
    main_appender.Close();
    connection->Commit();
    this->log_id = log_id.ToString();
    this->log_time = to_timepoint(log_time);
    return *this;
}
AllianceLog::AllianceLog() :
    log_id("00000000-0000-0000-0000-000000000000"),
    log_time(TimePoint(std::chrono::seconds(0))),
    id(0), name(""), rank(0), member_count(0), max_members(0), value(0.0), ipo(false), min_sv(0.0),
    members()
{}

AllianceLog::AllianceLog(const duckdb::unique_ptr<duckdb::DataChunk>& chunk, idx_t row) :
    log_id(chunk->GetValue(0, row).GetValue<string>()),
    log_time(to_timepoint(chunk->GetValue(1, row).GetValue<duckdb::timestamp_t>())),
    id(chunk->GetValue(2, row).GetValue<uint32_t>()),
    name(chunk->GetValue(3, row).GetValue<string>()),
    rank(chunk->GetValue(4, row).GetValue<uint32_t>()),
    member_count(chunk->GetValue(5, row).GetValue<uint8_t>()),
    max_members(chunk->GetValue(6, row).GetValue<uint8_t>()),
    value(chunk->GetValue(7, row).GetValue<double>()),
    ipo(chunk->GetValue(8, row).GetValue<bool>()),
    min_sv(chunk->GetValue(9, row).GetValue<float>()),
    members()
{
    auto memlist = chunk->GetValue(10, 0);
    for (auto &mem : duckdb::ListValue::GetChildren(memlist)) {
        auto &vals = duckdb::StructValue::GetChildren(mem);
        this->members.emplace_back(
            vals[0].GetValue<uint32_t>(),
            vals[1].GetValue<string>(),
            to_timepoint(vals[2].GetValue<duckdb::timestamp_t>()),
            vals[3].GetValue<uint32_t>(),
            vals[4].GetValue<uint32_t>(),
            vals[5].GetValue<uint32_t>(),
            to_timepoint(vals[6].GetValue<duckdb::timestamp_t>()),
            vals[7].GetValue<float>(),
            vals[8].GetValue<uint32_t>()
        );
    }
}

AllianceLog AllianceLog::from_log_id(const string& log_id) {
    auto result = Database::Client()->get_alliance_log_by_log_id->Execute(log_id.c_str());
    if (result->HasError()) throw DatabaseException(result->GetError());
    auto chunk = result->Fetch();
    return (chunk && chunk->size() > 0) ? AllianceLog(chunk, 0) : AllianceLog();
}



UserLog::Share::Share(const TimePoint& ts, float share) :
    ts(ts), share(share)
{}

UserLog::Award::Award(const TimePoint& ts, const string& award) :
    ts(ts), award(award)
{}

UserLog::AircraftCount::AircraftCount(const string& aircraft, int amount) :
    aircraft(aircraft), amount(amount),
    parsed_aircraft(Database::Client()->get_aircraft_by_name(aircraft, 0))
{}

UserLog::UserLog(
    uint32_t id, const string& username, uint16_t level, bool online, 
    float share, uint32_t shares_available, uint32_t shares_sold, bool ipo,
    uint16_t fleet_count, uint16_t routes, const string& alliance, 
    uint8_t achievements, bool game_mode, uint32_t rank, uint8_t reputation, uint8_t cargo_reputation,
    const TimePoint& founded, const string& logo,
    std::vector<Share> share_log, std::vector<Award> awards,
    std::vector<AircraftCount> fleet, std::vector<RouteDetail> route_list
) :
    id(id), username(username), level(level), online(online),
    share(share), shares_available(shares_available), shares_sold(shares_sold), ipo(ipo),
    fleet_count(fleet_count), routes(routes), alliance(alliance),
    achievements(achievements), game_mode(game_mode), rank(rank), reputation(reputation), cargo_reputation(cargo_reputation),
    founded(founded), logo(logo),
    share_log(share_log), awards(awards),
    fleet(fleet), route_list(route_list)
{}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

void pybind_init_log(py::module_& m) {
    py::module_ m_log = m.def_submodule("log");

    py::class_<AllianceLog> alliance_log_class(m_log, "AllianceLog");
    py::class_<AllianceLog::Member>(alliance_log_class, "Member")
        .def(
            py::init<uint32_t, const string&, const TimePoint&, uint32_t, uint64_t, uint32_t, const TimePoint&, float, uint32_t>(),
            "id"_a, "username"_a, "joined"_a, "flights"_a, "contributed"_a, "daily_contribution"_a, "online"_a, "sv"_a, "season"_a
        )
        .def_readonly("id", &AllianceLog::Member::id)
        .def_readonly("username", &AllianceLog::Member::username)
        .def_readonly("joined", &AllianceLog::Member::joined)
        .def_readonly("flights", &AllianceLog::Member::flights)
        .def_readonly("contributed", &AllianceLog::Member::contributed)
        .def_readonly("daily_contribution", &AllianceLog::Member::daily_contribution)
        .def_readonly("online", &AllianceLog::Member::online)
        .def_readonly("sv", &AllianceLog::Member::sv)
        .def_readonly("season", &AllianceLog::Member::season);

    alliance_log_class
        .def(
            py::init<uint32_t, const string&, uint32_t, uint8_t, uint8_t, double, bool, float, std::vector<AllianceLog::Member>>(),
            "id"_a, "name"_a, "rank"_a, "member_count"_a, "max_members"_a, "value"_a, "ipo"_a, "min_sv"_a, "members"_a
        )
        .def_readonly("log_id", &AllianceLog::log_id)
        .def_readonly("log_time", &AllianceLog::log_time)
        .def_readonly("id", &AllianceLog::id)
        .def_readonly("name", &AllianceLog::name)
        .def_readonly("rank", &AllianceLog::rank)
        .def_readonly("member_count", &AllianceLog::member_count)
        .def_readonly("max_members", &AllianceLog::max_members)
        .def_readonly("value", &AllianceLog::value)
        .def_readonly("ipo", &AllianceLog::ipo)
        .def_readonly("min_sv", &AllianceLog::min_sv)
        .def_readonly("members", &AllianceLog::members)
        .def("insert_to_db", &AllianceLog::insert_to_db)
        .def_static("from_log_id", &AllianceLog::from_log_id, "log_id"_a);

    py::class_<UserLog> user_log_class(m_log, "UserLog");

    py::class_<UserLog::Share>(user_log_class, "Share")
        .def(py::init<const TimePoint&, float>(), "ts"_a, "share"_a)
        .def_readonly("ts", &UserLog::Share::ts)
        .def_readonly("share", &UserLog::Share::share);

    py::class_<UserLog::Award>(user_log_class, "Award")
        .def(py::init<const TimePoint&, const string&>(), "ts"_a, "award"_a)
        .def_readonly("ts", &UserLog::Award::ts)
        .def_readonly("award", &UserLog::Award::award);

    py::class_<UserLog::AircraftCount>(user_log_class, "AircraftCount")
        .def_readonly("aircraft", &UserLog::AircraftCount::aircraft)
        .def_readonly("amount", &UserLog::AircraftCount::amount);

    py::class_<UserLog::RouteDetail>(user_log_class, "RouteDetail")
        .def_readonly("origin", &UserLog::RouteDetail::origin)
        .def_readonly("stopover", &UserLog::RouteDetail::stopover)
        .def_readonly("destination", &UserLog::RouteDetail::destination)
        .def_readonly("distance", &UserLog::RouteDetail::distance)
        .def_readonly("arrived", &UserLog::RouteDetail::arrived);

    user_log_class
        .def(
            py::init<
                uint32_t, const string&, uint16_t, bool,
                float, uint32_t, uint32_t, bool,
                uint16_t, uint16_t, const string&,
                uint8_t, bool, uint32_t, uint8_t, uint8_t,
                const TimePoint&, const string&,
                std::vector<UserLog::Share>, std::vector<UserLog::Award>,
                std::vector<UserLog::AircraftCount>, std::vector<UserLog::RouteDetail>
            >(),
            "id"_a, "username"_a, "level"_a, "online"_a,
            "share"_a, "shares_available"_a, "shares_sold"_a, "ipo"_a,
            "fleet_count"_a, "routes"_a, "alliance"_a,
            "achievements"_a, "game_mode"_a, "rank"_a, "reputation"_a, "cargo_reputation"_a,
            "founded"_a, "logo"_a,
            "share_log"_a, "awards"_a,
            "fleet"_a, "route_list"_a
        )
        .def_readonly("log_id", &UserLog::log_id)
        .def_readonly("log_time", &UserLog::log_time)
        .def_readonly("username", &UserLog::username)
        .def_readonly("level", &UserLog::level)
        .def_readonly("online", &UserLog::online)
        .def_readonly("share", &UserLog::share)
        .def_readonly("shares_available", &UserLog::shares_available)
        .def_readonly("shares_sold", &UserLog::shares_sold)
        .def_readonly("ipo", &UserLog::ipo)
        .def_readonly("fleet_count", &UserLog::fleet_count)
        .def_readonly("routes", &UserLog::routes)
        .def_readonly("alliance", &UserLog::alliance)
        .def_readonly("achievements", &UserLog::achievements)
        .def_readonly("game_mode", &UserLog::game_mode)
        .def_readonly("rank", &UserLog::rank)
        .def_readonly("reputation", &UserLog::reputation)
        .def_readonly("cargo_reputation", &UserLog::cargo_reputation)
        .def_readonly("founded", &UserLog::founded)
        .def_readonly("logo", &UserLog::logo)
        .def_readonly("share_log", &UserLog::share_log)
        .def_readonly("awards", &UserLog::awards)
        .def_readonly("fleet", &UserLog::fleet)
        .def_readonly("route_list", &UserLog::route_list);
}
#endif