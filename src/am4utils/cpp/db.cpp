#include <iostream>
#include <string>
#include <duckdb.hpp>
#include <algorithm>
#include <queue>

#include "include/db.hpp"
#include "include/ext/jaro.hpp"

using namespace duckdb;

shared_ptr<Database> Database::default_client = nullptr;
shared_ptr<Database> Database::Client(const string& home_dir, const string& db_name) {
    if (!default_client) {
        default_client = make_shared<Database>();
        default_client->database = make_uniq<DuckDB>(home_dir + "/data/" + db_name + ".db");
        default_client->connection = make_uniq<Connection>(*default_client->database);

        CHECK_SUCCESS(default_client->connection->Query("SET home_directory = '" + home_dir + "';"));
    }
    return default_client;
}
shared_ptr<Database> Database::Client() {
    if (!default_client) {
        Database::Client(".", "main");
    }
    return default_client;
}

void Database::populate_database() {
    CHECK_SUCCESS(connection->Query(
        "CREATE TABLE IF NOT EXISTS users ("
        "  id                UUID NOT NULL DEFAULT uuid(),"
        "  username          VARCHAR NOT NULL DEFAULT '',"
        "  password          VARCHAR NOT NULL DEFAULT '',"
        "  game_id           UBIGINT NOT NULL DEFAULT 0,"
        "  game_name         VARCHAR NOT NULL DEFAULT '',"
        "  game_mode         BOOLEAN NOT NULL DEFAULT FALSE,"
        "  discord_id        UBIGINT NOT NULL DEFAULT 0,"
        "  wear_training     UTINYINT NOT NULL DEFAULT 0,"
        "  repair_training   UTINYINT NOT NULL DEFAULT 0,"
        "  l_training        UTINYINT NOT NULL DEFAULT 0,"
        "  h_training        UTINYINT NOT NULL DEFAULT 0,"
        "  fuel_training     UTINYINT NOT NULL DEFAULT 0,"
        "  co2_training      UTINYINT NOT NULL DEFAULT 0,"
        "  fuel_price        USMALLINT NOT NULL DEFAULT 700,"
        "  co2_price         UTINYINT NOT NULL DEFAULT 120,"
        "  accumulated_count USMALLINT NOT NULL DEFAULT 0,"
        "  load              DOUBLE NOT NULL DEFAULT 0.87,"
        "  income_loss_tol   DOUBLE NOT NULL DEFAULT 0.0,"
        "  role              UTINYINT NOT NULL DEFAULT 0,"
        ");"
    ));
    CHECK_SUCCESS(connection->Query("CREATE INDEX IF NOT EXISTS users_idx ON users(id, username, game_id, game_name, discord_id);"));

    verify_user_by_username = connection->Prepare("SELECT id FROM users WHERE username = $1 LIMIT 1;");
    CHECK_SUCCESS_REF(verify_user_by_username);

    insert_user = connection->Prepare(INSERT_USER_STATEMENT);
    CHECK_SUCCESS_REF(insert_user);

    get_user_by_id = connection->Prepare(SELECT_USER_STATEMENT("id"));
    CHECK_SUCCESS_REF(get_user_by_id);

    get_user_by_username = connection->Prepare(SELECT_USER_STATEMENT("username"));
    CHECK_SUCCESS_REF(get_user_by_username);

    get_user_by_game_id = connection->Prepare(SELECT_USER_STATEMENT("game_id"));
    CHECK_SUCCESS_REF(get_user_by_game_id);

    get_user_by_game_name = connection->Prepare(SELECT_USER_STATEMENT("game_name"));
    CHECK_SUCCESS_REF(get_user_by_game_name);
    
    get_user_by_discord_id = connection->Prepare(SELECT_USER_STATEMENT("discord_id"));
    CHECK_SUCCESS_REF(get_user_by_discord_id);


    update_user_username = connection->Prepare("UPDATE users SET username = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_username);

    update_user_password = connection->Prepare("UPDATE users SET password = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_password);

    update_user_game_id = connection->Prepare("UPDATE users SET game_id = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_game_id);

    update_user_game_name = connection->Prepare("UPDATE users SET game_name = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_game_name);

    update_user_game_mode = connection->Prepare("UPDATE users SET game_mode = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_game_mode);

    update_user_discord_id = connection->Prepare("UPDATE users SET discord_id = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_discord_id);

    update_user_wear_training = connection->Prepare("UPDATE users SET wear_training = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_wear_training);

    update_user_repair_training = connection->Prepare("UPDATE users SET repair_training = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_repair_training);

    update_user_l_training = connection->Prepare("UPDATE users SET l_training = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_l_training);

    update_user_h_training = connection->Prepare("UPDATE users SET h_training = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_h_training);

    update_user_fuel_training = connection->Prepare("UPDATE users SET fuel_training = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_fuel_training);

    update_user_co2_training = connection->Prepare("UPDATE users SET co2_training = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_co2_training);

    update_user_fuel_price = connection->Prepare("UPDATE users SET fuel_price = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_fuel_price);

    update_user_co2_price = connection->Prepare("UPDATE users SET co2_price = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_co2_price);

    update_user_accumulated_count = connection->Prepare("UPDATE users SET accumulated_count = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_accumulated_count);

    update_user_load = connection->Prepare("UPDATE users SET load = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_load);

    update_user_income_tolerance = connection->Prepare("UPDATE users SET income_loss_tol = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_income_tolerance);

    update_user_role = connection->Prepare("UPDATE users SET role = $1 WHERE id = $2;");
    CHECK_SUCCESS_REF(update_user_role);
}

void Database::populate_internal() {
    auto result = connection->Query("SELECT * FROM read_parquet('~/data/airports.parquet');");
    CHECK_SUCCESS_REF(result);
    idx_t i = 0;
    while (auto chunk = result->Fetch()) {
        for (idx_t j = 0; j < chunk->size(); j++, i++) {
            airports[i] = Airport(chunk, j);
        }
    }
    const uint16_t apid_breakpoints[] = {
        52, 178, 248, 318, 538, 542, 544, 552, 558, 562,
        570, 572, 577, 597, 1110, 1130, 1162, 1200, 1249, 1265,
        1306, 1309, 1311, 1313, 1326, 1328, 1356, 1358, 1378, 1381,
        1388, 1391, 1468, 1481, 1513, 1528, 1532, 1537, 1540, 1541,
        1543, 1571, 1592, 1598, 1625, 1683, 1696, 2382, 2400, 2533,
        2557, 2559, 2566, 2573, 2577, 2591, 2597, 2610, 2627, 2630,
        2646, 2648, 2656, 2660, 2662, 2664, 2665, 2667, 2673, 3053,
        3194, 3506, 3508, 3550, 3899, 3982
    };
    uint16_t start_bp = 1, offset = 1;
    for (uint16_t bp : apid_breakpoints) {
        for (uint16_t i = start_bp; i <= bp; i++) {
            airport_id_hashtable[i] = i - offset;
        }
        offset++;
        start_bp = bp + 1;
    }

    result = connection->Query("SELECT * FROM read_parquet('~/data/aircrafts.parquet');");
    CHECK_SUCCESS_REF(result);
    i = 0;
    while (auto chunk = result->Fetch()) {
        for (uint16_t j = 0; j < chunk->size(); j++, i++) {
            aircrafts[i] = Aircraft(chunk, j);
        }
    }

    result = connection->Query("SELECT yd, jd, fd, d FROM read_parquet('~/data/routes.parquet');");
    CHECK_SUCCESS_REF(result);
    i = 0;
    uint16_t x = 0, y = 0;
    while (auto chunk = result->Fetch()) {
        for (idx_t j = 0; j < chunk->size(); j++, i++) {
            pax_demands[i] = PaxDemand(
                chunk->GetValue(0, j).GetValue<uint16_t>(),
                chunk->GetValue(1, j).GetValue<uint16_t>(),
                chunk->GetValue(2, j).GetValue<uint16_t>()
            );
            y++;
            if (y == AIRPORT_COUNT) {
                x++;
                y = x + 1;
            }
            const double distance = chunk->GetValue(3, j).GetValue<double>();
            distances[x][y] = distance;
            distances[y][x] = distance;
        }
    }
}

const uint16_t missing_ids[] = {
    52,178,248,318,538,542,544,552,558,562,
    571,572,577,597,1110,1130,1162,1200,1249,1265,1306,
    1310,1311,1313,1326,1328,1356,1358,1378,1381,1388,1391,
    1468,1481,1513,1528,1532,1537,1540,1542,1543,1571,1592,
    1598,1625,1683,1696,2382,2400,2533,2557,2559,2566,2573,
    2577,2591,2597,2610,2627,2630,2647,2648,2656,2660,2662,
    2664,2666,2667,2673,3053,3194,3507,3508,3550,3899
};
Airport Database::get_airport_by_id(uint16_t id) {
    if (std::find(std::begin(missing_ids), std::end(missing_ids), id) != std::end(missing_ids)) return Airport();
    if (id > 3982) return Airport();
    return airports[airport_id_hashtable[id]];
}

Airport Database::get_airport_by_iata(const std::string& iata) {
    auto it = std::find_if(std::begin(airports), std::end(airports), [&](const Airport& a) {
        return a.iata == iata;
    });
    return it == std::end(airports) ? Airport() : *it;
}

Airport Database::get_airport_by_icao(const std::string& icao) {
    auto it = std::find_if(std::begin(airports), std::end(airports), [&](const Airport& a) {
        return a.icao == icao;
    });
    return it == std::end(airports) ? Airport() : *it;
}

Airport Database::get_airport_by_name(const std::string& name) {
    auto it = std::find_if(std::begin(airports), std::end(airports), [&](const Airport& a) {
        string db_name = a.name;
        std::transform(db_name.begin(), db_name.end(), db_name.begin(), ::toupper);
        return db_name == name;
    });
    return it == std::end(airports) ? Airport() : *it;
}

Airport Database::get_airport_by_all(const std::string& all) {
    try {
        uint16_t id = static_cast<uint16_t>(std::stoi(all));
        Airport ap = get_airport_by_id(id);
        if (ap.valid) return ap;
    } catch (std::invalid_argument& e) {
    }
    auto it = std::find_if(std::begin(airports), std::end(airports), [&](const Airport& a) {
        string db_name = a.name;
        std::transform(db_name.begin(), db_name.end(), db_name.begin(), ::toupper);
        return a.iata == all || a.icao == all || db_name == all;
    });
    return it == std::end(airports) ? Airport() : *it;
}

std::vector<Airport::Suggestion> Database::suggest_airport_by_iata(const std::string& iata) {
    std::priority_queue<Airport::Suggestion, std::vector<Airport::Suggestion>, CompareSuggestion> pq;
    for (const Airport& ap : airports) {
        double score = jaro_winkler_distance(iata, ap.iata);
        if (pq.size() < 5) {
            pq.emplace(std::make_shared<Airport>(ap), score);
        } else if (score > pq.top().score) {
            pq.pop();
            pq.emplace(std::make_shared<Airport>(ap), score);
        }
    }
    std::vector<Airport::Suggestion> suggestions;
    while (!pq.empty()) {
        suggestions.insert(suggestions.begin(), pq.top());
        pq.pop();
    }
    return suggestions;
}

std::vector<Airport::Suggestion> Database::suggest_airport_by_icao(const std::string& icao) {
    std::priority_queue<Airport::Suggestion, std::vector<Airport::Suggestion>, CompareSuggestion> pq;
    for (const Airport& ap : airports) {
        double score = jaro_winkler_distance(icao, ap.icao);
        if (pq.size() < 5) {
            pq.emplace(std::make_shared<Airport>(ap), score);
        } else if (score > pq.top().score) {
            pq.pop();
            pq.emplace(std::make_shared<Airport>(ap), score);
        }
    }
    std::vector<Airport::Suggestion> suggestions;
    while (!pq.empty()) {
        suggestions.insert(suggestions.begin(), pq.top());
        pq.pop();
    }
    return suggestions;
}

std::vector<Airport::Suggestion> Database::suggest_airport_by_name(const std::string& name) {
    std::priority_queue<Airport::Suggestion, std::vector<Airport::Suggestion>, CompareSuggestion> pq;
    for (const Airport& ap : airports) {
        string ap_name = ap.name;
        std::transform(ap_name.begin(), ap_name.end(), ap_name.begin(), ::toupper);
        double score = jaro_winkler_distance(name, ap_name);
        if (pq.size() < 5) {
            pq.emplace(std::make_shared<Airport>(ap), score);
        } else if (score > pq.top().score) {
            pq.pop();
            pq.emplace(std::make_shared<Airport>(ap), score);
        }
    }
    std::vector<Airport::Suggestion> suggestions;
    while (!pq.empty()) {
        suggestions.insert(suggestions.begin(), pq.top());
        pq.pop();
    }
    return suggestions;
}

std::vector<Airport::Suggestion> Database::suggest_airport_by_all(const std::string& all) {
    std::priority_queue<Airport::Suggestion, std::vector<Airport::Suggestion>, CompareSuggestion> pq;
    for (const Airport& ap : airports) {
        string ap_name = ap.name;
        std::transform(ap_name.begin(), ap_name.end(), ap_name.begin(), ::toupper);
        double score = std::max(
            std::max(jaro_winkler_distance(all, ap.iata), jaro_winkler_distance(all, ap.icao)),
            jaro_winkler_distance(all, ap_name)
        );
        if (pq.size() < 5) {
            pq.emplace(std::make_shared<Airport>(ap), score);
        } else if (score > pq.top().score) {
            pq.pop();
            pq.emplace(std::make_shared<Airport>(ap), score);
        }
    }
    std::vector<Airport::Suggestion> suggestions;
    while (!pq.empty()) {
        suggestions.insert(suggestions.begin(), pq.top());
        pq.pop();
    }
    return suggestions;
}


uint16_t Database::get_aircraft_idx_by_id(uint16_t id, uint8_t priority) {
    const std::map<uint16_t, uint16_t> idx_id_map{
        {1,0},{2,4},{3,7},{4,8},{5,10},{6,12},{7,14},{8,17},{9,21},{10,22},
        {11,23},{12,24},{13,25},{14,29},{15,30},{16,32},{17,34},{18,36},{19,37},{20,38},
        {21,39},{22,41},{23,42},{24,43},{25,46},{26,47},{27,48},{28,49},{29,50},{30,51},
        {31,52},{32,53},{33,57},{34,59},{35,60},{36,61},{37,64},{38,66},{39,69},{40,72},
        {41,73},{42,74},{43,75},{44,76},{45,77},{46,78},{47,79},{48,81},{49,82},{50,84},
        {51,85},{52,89},{53,93},{55,99},{56,105},{58,106},{59,107},{60,108},{61,109},{62,112},
        {63,115},{64,118},{66,120},{67,122},{68,124},{69,127},{71,129},{72,133},{73,137},{74,140},
        {75,143},{76,146},{85,147},{86,148},{87,149},{89,151},{90,152},{91,153},{92,154},{93,155},
        {94,157},{95,158},{96,159},{97,160},{99,161},{100,162},{101,163},{102,164},{103,166},{104,167},
        {105,168},{106,169},{107,170},{108,171},{109,172},{110,173},{111,174},{112,175},{113,178},{114,180},
        {115,182},{116,183},{117,184},{118,185},{119,186},{120,187},{124,190},{126,191},{127,192},{128,193},
        {129,194},{130,195},{131,196},{132,197},{133,198},{134,199},{135,200},{136,201},{137,202},{138,203},
        {139,204},{140,205},{141,206},{142,207},{143,208},{144,209},{145,210},{146,211},{147,212},{148,213},
        {149,214},{150,216},{151,217},{152,218},{153,219},{154,220},{155,221},{156,222},{157,223},{158,224},
        {159,225},{160,226},{161,227},{162,228},{163,229},{164,230},{165,231},{166,232},{167,234},{168,235},
        {169,236},{170,238},{171,241},{172,242},{173,243},{177,246},{178,247},{179,248},{180,249},{181,250},
        {182,251},{183,252},{184,253},{185,254},{186,255},{187,256},{189,257},{190,258},{191,259},{192,260},
        {193,261},{194,262},{195,264},{196,265},{197,266},{198,267},{199,268},{200,269},{201,270},{202,272},
        {203,273},{204,274},{205,276},{206,277},{207,278},{208,279},{209,280},{210,281},{211,282},{212,283},
        {213,284},{214,285},{215,286},{216,287},{218,288},{219,289},{220,290},{221,291},{222,292},{226,293},
        {227,296},{228,299},{229,300},{230,303},{231,304},{232,305},{233,307},{234,309},{241,310},{242,313},
        {243,319},{244,320},{245,322},{246,323},{247,324},{248,325},{249,326},{250,328},{251,329},{252,330},
        {253,331},{254,332},{255,333},{256,334},{257,335},{258,336},{259,337},{260,338},{266,339},{267,340},
        {268,341},{269,343},{270,344},{271,345},{272,348},{273,349},{274,350},{275,351},{276,352},{277,354},
        {281,355},{282,356},{283,357},{284,358},{285,359},{287,360},{288,362},{289,363},{290,364},{291,365},
        {292,366},{293,367},{294,368},{295,369},{298,370},{299,371},{300,372},{302,374},{303,377},{304,379},
        {305,380},{306,381},{307,383},{308,384},{309,385},{310,386},{311,390},{312,394},{313,395},{314,396},
        {315,397},{316,399},{317,400},{318,401},{320,405},{321,407},{322,409},{323,413},{324,417},{325,418},
        {326,419},{327,420},{328,421},{329,422},{330,423},{331,424},{332,425},{333,426},{334,427},{335,428},
        {336,432},{337,434},{338,435},{339,436},{340,438},{341,439},{342,440},{343,441},{344,442},{345,443},
        {346,444},{347,445},{348,446},{349,447},{350,448},{351,449},{352,450},{353,451},{355,453},{356,454},
        {357,455},{358,457},{359,459},{360,460},{361,464},{362,468},{363,471},{364,474},{365,475},{366,477},
        {367,479},{368,480},{369,482},{370,483},{371,484},{372,485},{373,486}
    };
    auto search = idx_id_map.find(id);
    if (search != idx_id_map.end()) {
        auto next = std::next(search);
        if (next != idx_id_map.end()) {
            if (priority > next->second - search->second - 1) priority = 0;
        }
        return search->second + priority;
    }
    return 0;
}

Aircraft Database::get_aircraft_by_id(uint16_t id, uint8_t priority) {
    const uint16_t missing_ids[] = {
        54,57,65,70,77,78,79,80,81,82,
        83,84,88,98,121,122,123,125,174,175,
        176,188,217,223,224,225,235,236,237,
        238,239,240,261,262,263,264,265,278,
        279,280,286,296,297,301,319,354
    };
    if (std::find(std::begin(missing_ids), std::end(missing_ids), id) != std::end(missing_ids)) return Aircraft();
    if (id > 373) return Aircraft();
    return aircrafts[Database::get_aircraft_idx_by_id(id, priority)];
}

Aircraft Database::get_aircraft_by_shortname(const string& shortname, uint8_t priority) {
    auto it = std::find_if(std::begin(aircrafts), std::end(aircrafts), [&](const Aircraft& a) {
        return a.shortname == shortname && a.priority == priority;
    });
    return it == std::end(aircrafts) ? Aircraft() : *it;
}

Aircraft Database::get_aircraft_by_name(const string& name, uint8_t priority) {
    auto it = std::find_if(std::begin(aircrafts), std::end(aircrafts), [&](const Aircraft& a) {
        string db_name = a.name;
        std::transform(db_name.begin(), db_name.end(), db_name.begin(), ::tolower);
        return db_name == name && a.priority == priority;
    });
    return it == std::end(aircrafts) ? Aircraft() : *it;
}

Aircraft Database::get_aircraft_by_all(const string& shortname, uint8_t priority) {
    try {
        uint16_t id = static_cast<uint16_t>(std::stoi(shortname));
        Aircraft ac = get_aircraft_by_id(id, 0);
        if (ac.valid) return ac;
    } catch (std::invalid_argument& e) {
    }
    auto it = std::find_if(std::begin(aircrafts), std::end(aircrafts), [&](const Aircraft& a) {
        string db_name = a.name;
        std::transform(db_name.begin(), db_name.end(), db_name.begin(), ::tolower);
        return (a.shortname == shortname || db_name == shortname) && a.priority == priority;
    });
    return it == std::end(aircrafts) ? Aircraft() : *it;
}

std::vector<Aircraft::Suggestion> Database::suggest_aircraft_by_shortname(const string& name) {
    std::priority_queue<Aircraft::Suggestion, std::vector<Aircraft::Suggestion>, CompareSuggestion> pq;
    for (const Aircraft& ac : aircrafts) {
        if (ac.priority != 0) continue;
        double score = jaro_winkler_distance(name, ac.shortname);
        if (pq.size() < 5) {
            pq.emplace(std::make_shared<Aircraft>(ac), score);
        } else if (score > pq.top().score) {
            pq.pop();
            pq.emplace(std::make_shared<Aircraft>(ac), score);
        }
    }
    std::vector<Aircraft::Suggestion> suggestions;
    while (!pq.empty()) {
        suggestions.insert(suggestions.begin(), pq.top());
        pq.pop();
    }
    return suggestions;
}

std::vector<Aircraft::Suggestion> Database::suggest_aircraft_by_name(const string& name) {
    std::priority_queue<Aircraft::Suggestion, std::vector<Aircraft::Suggestion>, CompareSuggestion> pq;
    for (const Aircraft& ac : aircrafts) {
        if (ac.priority != 0) continue;
        string ac_name = ac.name;
        std::transform(ac_name.begin(), ac_name.end(), ac_name.begin(), ::tolower);
        double score = jaro_winkler_distance(name, ac_name);
        if (pq.size() < 5) {
            pq.emplace(std::make_shared<Aircraft>(ac), score);
        } else if (score > pq.top().score) {
            pq.pop();
            pq.emplace(std::make_shared<Aircraft>(ac), score);
        }
    }
    std::vector<Aircraft::Suggestion> suggestions;
    while (!pq.empty()) {
        suggestions.insert(suggestions.begin(), pq.top());
        pq.pop();
    }
    return suggestions;
}

std::vector<Aircraft::Suggestion> Database::suggest_aircraft_by_all(const string& all) {
    std::priority_queue<Aircraft::Suggestion, std::vector<Aircraft::Suggestion>, CompareSuggestion> pq;
    for (const Aircraft& ac : aircrafts) {
        if (ac.priority != 0) continue;
        string ac_name = ac.name;
        std::transform(ac_name.begin(), ac_name.end(), ac_name.begin(), ::tolower);
        double score = std::max(jaro_winkler_distance(all, ac.shortname), jaro_winkler_distance(all, ac_name));
        if (pq.size() < 5) {
            pq.emplace(std::make_shared<Aircraft>(ac), score);
        } else if (score > pq.top().score) {
            pq.pop();
            pq.emplace(std::make_shared<Aircraft>(ac), score);
        }
    }

    std::vector<Aircraft::Suggestion> suggestions;
    while (!pq.empty()) {
        suggestions.insert(suggestions.begin(), pq.top());
        pq.pop();
    }
    return suggestions;
}

void init(string home_dir, string db_name) {
    auto client = Database::Client(home_dir, db_name);
    client->populate_internal();
    client->populate_database();
}

void reset() {
    auto client = Database::Client();
    CHECK_SUCCESS(client->connection->Query("DROP TABLE users;"));
    client->populate_database();
}

void _debug_query(string query) {
    auto client = Database::Client();

    auto result = client->connection->Query(query);
    result->Print();
    // while (auto chunk = result->Fetch()) {
    //     chunk->Print();
    // }
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"
#include <optional>
#include <filesystem>

void pybind_init_db(py::module_& m) {
    py::module_ m_db = m.def_submodule("db");

    m_db
        .def("init", [](std::optional<string> home_dir, std::optional<string> db_name) {
            py::gil_scoped_acquire acquire;
            string db_name_str = db_name.value_or("main");
            if (!home_dir.has_value()) {
                string hdir = py::module::import("am4utils").attr("__path__").cast<py::list>()[0].cast<string>(); // am4utils.__path__[0]
                py::function urlretrieve = py::module::import("urllib.request").attr("urlretrieve");
                if (!std::filesystem::exists(hdir + "/data")) {
                    std::cout << "WARN: data directory not found, creating..." << std::endl;
                    std::filesystem::create_directory(hdir + "/data");
                }
                for (const std::string fn : {"airports.parquet", "aircrafts.parquet", "routes.parquet"}) {
                    if (!std::filesystem::exists(hdir + "/data/" + fn)) {
                        std::cout << "WARN: " << fn << " not found, downloading from GitHub..." << std::endl;
                        urlretrieve(
                            "https://github.com/cathaypacific8747/am4bot/releases/latest/download/" + fn,
                            hdir + "/data/" + fn
                        );
                    }
                }
                init(hdir, db_name_str);
            } else {
                init(home_dir.value(), db_name_str);
            }
            py::gil_scoped_release release;
        }, "home_dir"_a = py::none(), "db_name"_a = "main")
        .def("reset", &reset)
        .def("_debug_query", &_debug_query, "query"_a);

    py::register_exception<DatabaseException>(m_db, "DatabaseException");
}
#endif