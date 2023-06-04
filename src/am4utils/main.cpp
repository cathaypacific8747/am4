#include "include/enums.h"
#include "include/db.hpp"
#include "include/airport.hpp"
#include "include/aircraft.hpp"
#include "include/route.hpp"
#include <fstream>
#include <sstream>
#include <vector>
#include <iostream>
#include <iomanip>
#include <chrono>

using std::string;
using std::cout;
using std::cerr;
using std::endl;

#ifdef VERSION_INFO
    string version = MACRO_STRINGIFY(VERSION_INFO);
#else
    string version = "dev";
#endif

#ifdef CORE_DIR
    string core_dir = MACRO_STRINGIFY(CORE_DIR);
#else
    string core_dir = ""
#endif

// benchmark time
#define START_TIMER auto start = std::chrono::high_resolution_clock::now();
#define END_TIMER auto finish = std::chrono::high_resolution_clock::now(); \
    std::chrono::duration<double> elapsed = finish - start; \
    cout << "elapsed: " << elapsed.count() * 1000 << " ms\n";

void test_route_distance() {
    std::vector<Airport> airports;
    for (int i = 0; i <= 3983; i++) {
        auto ap = Airport::_from_id(i);
        if (ap.id == 0) continue;
        airports.push_back(ap);
    }

    START_TIMER
    for (int i = 0; i < airports.size(); i++) {
        for (int j = 0; j < airports.size(); j++) {
            if (i >= j) continue;
            double distance = Route::calc_distance(airports[i], airports[j]);
        }
    }
    END_TIMER // 1.171483 s
}

void test_demand_queries() {
    srand(1);
    auto con = Database::Client();
    auto routes_query = con->connection->Prepare("SELECT * FROM routes WHERE yd > ? AND jd > ? AND fd > ? AND d < ?;");

    int64_t total_rows = 0;
    START_TIMER
    for (int i = 0; i < 100000; i++) {
        total_rows += routes_query->Execute(292, 193, 80, 14943)->Fetch()->size();
    }
    END_TIMER // .145 ms/it
    cout << "total fetched rows: " << total_rows << endl;
}

void fix_routes_csv() {
    std::vector<Airport> airports;
    for (int i = 0; i <= 3983; i++) {
        auto ap = Airport::_from_id(i);
        airports.push_back(ap);
    }
    cout << "loaded airports" << endl;

    std::ifstream infile("C:/Users/cx/projects/am4bot/research/web/routes.csv");
    if (!infile.is_open()) {
        cerr << "Error opening infile" << endl;
    }

    std::ofstream outfile("C:/Users/cx/projects/am4bot/research/web/routes.fixed.csv");
    if (!outfile.is_open()) {
        cerr << "Error opening infile" << endl;
    }

    string line;
    idx_t i = 0;
    while (std::getline(infile, line)) {
        std::vector<string> route;
        std::stringstream ss(line);
        string item;

        while (std::getline(ss, item, ',')) {
            route.push_back(item);
        }
        int16_t oid = stoi(route[0]);
        int16_t did = stoi(route[1]);
        double distance = Route::calc_distance(airports[oid], airports[did]);

        outfile << oid << "," << did << "," << route[2] << "," << route[3] << "," << route[4] << "," << distance << endl;

        if (i % 50 == 0) cout << "processed " << i << " routes" << endl;
        i++;
    }

    outfile.close();
}

int main(int argc, string argv[]) {
    cout << "am4utils (v" << version << "), home_directory " << core_dir << "\n_______" << std::setprecision(15) << endl;

    init(); // 1.3s
    // test_route_distance();
    // test_demand_queries();
    // fix_routes_csv();

    // PaxTicket pt = PaxTicket::from_optimal(10000, GameMode::EASY);
    // cout << pt.y << " | " << pt.j << " | " << pt.f << endl;
    
    // test_route_distance();

    Airport ap0 = Airport::from_auto("VHHH");
    Airport ap1 = Airport::from_auto("LHR");
    Route r = Route::from_airports(ap0, ap1);
    cout << r.origin.name << " -> " << r.destination.name << ": " << r.distance << "km, " << r.pax_demand.y << '/' << r.pax_demand.j << '/' << r.pax_demand.f << endl;
    cout << ap0.repr() << endl;
    cout << ap1.repr() << endl;
    try {
        Airport a = Airport::from_auto("VHHX");
    } catch (const AirportNotFoundException& e) {
        cerr << e.what() << endl;
    }

    return 0;
}