#include "include/db.hpp"
#include "include/airport.hpp"
#include <iostream>

using namespace std;

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

int main(int argc, string argv[]) {
    cout << "am4utils (v" << version << "), home_directory " << core_dir << endl;

    init();
    // _query("SELECT * FROM airports WHERE id < 4;");

    cout << "Airport::from_id(1)" << endl;
    Airport::from_id(1);
    return 0;
}