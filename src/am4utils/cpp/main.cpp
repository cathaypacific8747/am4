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

    Aircraft ac = *Aircraft::search("b744").ac;
    Airport ap0 = *Airport::search("vhhh").ap;
    Airport ap1 = *Airport::search("egll").ap;
    AircraftRoute ar = Route::create(ap0, ap1).assign(ac);
    cout << AircraftRoute::repr(ar) << endl;

    } catch (DatabaseException &e) {
        cerr << "DatabaseException: " << e.what() << endl;
        return 1;
    }
    return 0;
}