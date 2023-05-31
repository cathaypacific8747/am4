#include <duckdb.hpp>
#include <vector>

using namespace std;
using namespace duckdb;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#ifdef CORE_DIR
static string home_dir = MACRO_STRINGIFY(CORE_DIR);
#else
static string home_dir = "";
#endif

struct DatabaseConnection {
public:
    shared_ptr<DuckDB> database;
    shared_ptr<Connection> connection;
    std::vector<shared_ptr<DatabaseConnection>> connections;

    static shared_ptr<DatabaseConnection> DefaultConnection();

    shared_ptr<DatabaseConnection> Clone();
    void CloseAll();
    
    static shared_ptr<DatabaseConnection> CreateNewInstance();
    static shared_ptr<DatabaseConnection> default_connection;

    bool prepare_db();
};

static DuckDB db(":memory:");

bool init();
void _debug_query(string query);