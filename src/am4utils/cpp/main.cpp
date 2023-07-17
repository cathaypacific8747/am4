#include <fstream>
#include <sstream>
#include <vector>
#include <iostream>
#include <iomanip>
#include <chrono>

#include "include/db.hpp"
#include "include/game.hpp"
#include "include/ticket.hpp"
#include "include/demand.hpp"

#include "include/airport.hpp"
#include "include/aircraft.hpp"
#include "include/route.hpp"

using std::string;
using std::cout;
using std::cerr;
using std::endl;

#ifdef VERSION_INFO
    string version = MACRO_STRINGIFY(VERSION_INFO);
#else
    string version = "dev";
#endif

// string::size_type pos = string(result).find_last_of("\\/");
// return string(result).substr(0, pos);

#ifdef _WIN32
#include <Windows.h>
string get_executable_path() {
    char result[MAX_PATH];
    GetModuleFileName(NULL, result, MAX_PATH);
    string::size_type pos = string(result).find_last_of("\\/");
    return string(result).substr(0, pos);
}
#else
#include <unistd.h>
#include <limits.h>
string get_executable_path() {
    char result[PATH_MAX];
    ssize_t count = readlink("/proc/self/exe", result, PATH_MAX);
    string::size_type pos = string(result).find_last_of("\\/");
    return string(result).substr(0, pos);
}
#endif

// benchmark time
#define START_TIMER auto start = std::chrono::high_resolution_clock::now();
#define END_TIMER auto finish = std::chrono::high_resolution_clock::now(); \
    std::chrono::duration<double> elapsed = finish - start; \
    cout << "elapsed: " << elapsed.count() * 1000 << " ms\n";

int main() {
    string executable_path = get_executable_path();
    cout << "am4utils (v" << version << "), executable_path: " << executable_path << "\n_______" << std::setprecision(15) << endl;

    try {
    init(executable_path); // 1.3s
    // cout << "initialised database" << endl;
    // _debug_query("SELECT current_setting('home_directory')");

    // Campaign campaign = Campaign::Default();
    // cout << campaign.estimate_pax_reputation() << endl;

    START_TIMER
    // Aircraft ac = *Aircraft::search("mc214").ac;
    // Airport ap0 = *Airport::search("id:3500").ap;
    // Airport ap1 = *Airport::search("EGLLL").ap;
    // AircraftRoute ar = AircraftRoute::create(ap0, ap1, ac);
    // cout << AircraftRoute::repr(ar) << endl;
    
    // const auto& db = Database::Client();
    auto ap = Aircraft::search("id:1[1,sc]");
    cout << Aircraft::repr(*ap.ac) << endl;
    cout << ap.parse_result.priority;
    // auto ac_sugg = Aircraft::suggest(ap.parse_result);
    // for (auto &s : ac_sugg) {
    //     cout << Aircraft::repr(*s.ac) << s.score << endl;
    // }
    END_TIMER

    } catch (DatabaseException &e) {
        cerr << "DatabaseException: " << e.what() << endl;
        return 1;
    }
    return 0;
}