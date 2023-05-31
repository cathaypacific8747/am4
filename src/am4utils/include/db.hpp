#include <duckdb.hpp>

using namespace std;
using namespace duckdb;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#ifdef CORE_DIR
static string home_dir = MACRO_STRINGIFY(CORE_DIR);
#else
static string home_dir = "";
#endif

static DuckDB db(":memory:");

bool init();
void _query(string query);
Connection _get_connection();