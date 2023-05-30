#include <duckdb.hpp>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#ifdef CORE_DIR
static std::string home_dir = MACRO_STRINGIFY(CORE_DIR);
#else
static std::string home_dir = "";
#endif

static duckdb::DuckDB db(nullptr);

bool init_db();
void query_db(std::string query);