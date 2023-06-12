#include <iostream>

#include "include/db.hpp"
#include "include/aircraft.hpp"

using std::string;

Aircraft::Aircraft() : valid(false) {}

Aircraft::Aircraft(const duckdb::DataChunk& chunk, idx_t row) : 
    id(chunk.GetValue(0, row).GetValue<uint16_t>()),
    shortname(chunk.GetValue(1, row).GetValue<string>()),
    manufacturer(chunk.GetValue(2, row).GetValue<string>()),
    name(chunk.GetValue(3, row).GetValue<string>()),
    type(static_cast<AircraftType>(chunk.GetValue(4, row).GetValue<uint8_t>())),
    priority(chunk.GetValue(5, row).GetValue<uint8_t>()),
    eid(chunk.GetValue(6, row).GetValue<uint16_t>()),
    ename(chunk.GetValue(7, row).GetValue<string>()),
    speed(chunk.GetValue(8, row).GetValue<float>()),
    fuel(chunk.GetValue(9, row).GetValue<float>()),
    co2(chunk.GetValue(10, row).GetValue<float>()),
    cost(chunk.GetValue(11, row).GetValue<uint32_t>()),
    capacity(chunk.GetValue(12, row).GetValue<uint32_t>()),
    rwy(chunk.GetValue(13, row).GetValue<uint16_t>()),
    check_cost(chunk.GetValue(14, row).GetValue<uint32_t>()),
    range(chunk.GetValue(15, row).GetValue<uint16_t>()),
    ceil(chunk.GetValue(16, row).GetValue<uint16_t>()),
    maint(chunk.GetValue(17, row).GetValue<uint16_t>()),
    pilots(chunk.GetValue(18, row).GetValue<uint8_t>()),
    crew(chunk.GetValue(19, row).GetValue<uint8_t>()),
    engineers(chunk.GetValue(20, row).GetValue<uint8_t>()),
    technicians(chunk.GetValue(21, row).GetValue<uint8_t>()),
    img(chunk.GetValue(22, row).GetValue<string>()),
    wingspan(chunk.GetValue(23, row).GetValue<uint8_t>()),
    length(chunk.GetValue(24, row).GetValue<uint8_t>()),
    valid(true)
{};

Aircraft Aircraft::_from_id(uint16_t id, uint8_t priority) {
    auto result = Database::Client()->get_aircraft_by_id->Execute(id, priority);
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Aircraft();

    return Aircraft(*chunk, 0);
}

Aircraft Aircraft::_from_shortname(const string& shortname, uint8_t priority) {
    auto result = Database::Client()->get_aircraft_by_shortname->Execute(shortname.c_str(), priority);
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Aircraft();

    return Aircraft(*chunk, 0);
}

// TODO: also search for concat(manufacturer, ' ', name)?
Aircraft Aircraft::_from_name(const string& s, uint8_t priority) {
    auto result = Database::Client()->get_aircraft_by_name->Execute(s.c_str(), priority);
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Aircraft();

    return Aircraft(*chunk, 0);
}

Aircraft Aircraft::_from_all(const string& s, uint8_t priority) {
    auto result = Database::Client()->get_aircraft_by_all->Execute(s.c_str(), priority);
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Aircraft();

    return Aircraft(*chunk, 0);
}


std::vector<Aircraft> Aircraft::_suggest_shortname(const string& s, uint8_t priority) {
    std::vector<Aircraft> aircrafts;
    auto result = Database::Client()->suggest_aircraft_by_shortname->Execute(s.c_str(), priority);
    CHECK_SUCCESS(result);
    while (auto chunk = result->Fetch()) {
        for (idx_t i = 0; i < chunk->size(); i++) {
            aircrafts.emplace_back(*chunk, i);
        }
    }
    return aircrafts;
}

std::vector<Aircraft> Aircraft::_suggest_name(const string& s, uint8_t priority) {
    std::vector<Aircraft> aircrafts;
    auto result = Database::Client()->suggest_aircraft_by_name->Execute(s.c_str(), priority);
    CHECK_SUCCESS(result);
    while (auto chunk = result->Fetch()) {
        for (idx_t i = 0; i < chunk->size(); i++) {
            aircrafts.emplace_back(*chunk, i);
        }
    }
    return aircrafts;
}

// TODO: remove duplicates
std::vector<Aircraft> Aircraft::_suggest_all(const string& s, uint8_t priority) {
    std::vector<Aircraft> aircrafts;
    std::vector<AircraftSuggestion> suggestions;
    for (auto& stmt : {
        Database::Client()->suggest_aircraft_by_shortname.get(),
        Database::Client()->suggest_aircraft_by_name.get(),
    }) {
        auto result = stmt->Execute(s.c_str(), priority);
        CHECK_SUCCESS(result);
        auto chunk = result->Fetch();
        if (!chunk || chunk->size() == 0) continue;

        for (idx_t i = 0; i < chunk->size(); i++) {
            suggestions.emplace_back(
                Aircraft(*chunk, i),
                chunk->GetValue(5, i).GetValue<double>()
            );
        }
    }

    std::partial_sort(suggestions.begin(), suggestions.begin() + 5, suggestions.end(), [](const AircraftSuggestion& a, const AircraftSuggestion& b) {
        return a.score > b.score;
    });

    for (size_t i = 0; i < std::min<size_t>(5, suggestions.size()); i++) {
        aircrafts.push_back(std::move(suggestions[i].ac));
    }

    return aircrafts;
}


Aircraft Aircraft::from_auto(string s) {
    Aircraft ac;
    AircraftSearchType search_type = AircraftSearchType::ALL;

    string s_lower = s;
    std::transform(s_lower.begin(), s_lower.end(), s_lower.begin(), ::tolower);

    // search airports
    if (s_lower.substr(0, 5) == "name:") {
        search_type = AircraftSearchType::NAME;
        s = s_lower.substr(5);
        ac = Aircraft::_from_name(s);
    } else if (s_lower.substr(0, 10) == "shortname:") {
        search_type = AircraftSearchType::SHORTNAME;
        s = s_lower.substr(10);
        ac = Aircraft::_from_shortname(s);
    } else if (s_lower.substr(0, 4) == "all:") {
        s = s_lower.substr(4);
        ac = Aircraft::_from_all(s);
    } else if (s_lower.substr(0, 3) == "id:") {
        search_type = AircraftSearchType::ID;
        s = s.substr(3);
        try {
            ac = Aircraft::_from_id(std::stoi(s));
        } catch (std::invalid_argument& e) {
        } catch (std::out_of_range& e) { // silently skipping, empty suggestions will be thrown later on
        }
    } else {
        s = s_lower;
        ac = Aircraft::_from_all(s);
    }

    if (ac.valid) return ac;
    
    // empty airports, suggest and throw error
    std::vector<Aircraft> aircrafts;
    switch (search_type) {
        case AircraftSearchType::ALL:
            aircrafts = Aircraft::_suggest_all(s);
            break;
        case AircraftSearchType::NAME:
            aircrafts = Aircraft::_suggest_name(s);
            break;
        case AircraftSearchType::SHORTNAME:
            aircrafts = Aircraft::_suggest_shortname(s);
            break;
    }

    throw AircraftNotFoundException(search_type, s, aircrafts);
}

const string Aircraft::repr() {
    return "<Aircraft id=" + std::to_string(id) + " shortname='" + shortname + "' manufacturer='" + manufacturer + "' name='" + name + "' type=" + std::to_string(type) + " priority=" + std::to_string(priority) + " eid=" + std::to_string(eid) + " ename='" + ename + "' speed=" + std::to_string(speed) + " fuel=" + std::to_string(fuel) + " co2=" + std::to_string(co2) + " cost=" + std::to_string(cost) + " capacity=" + std::to_string(capacity) + " rwy=" + std::to_string(rwy) + " check_cost=" + std::to_string(check_cost) + " range=" + std::to_string(range) + " ceil=" + std::to_string(ceil) + " maint=" + std::to_string(maint) + " pilots=" + std::to_string(pilots) + " crew=" + std::to_string(crew) + " engineers=" + std::to_string(engineers) + " technicians=" + std::to_string(technicians) + " img='" + img + "' wingspan=" + std::to_string(wingspan) + " length=" + std::to_string(length) + ">";
}