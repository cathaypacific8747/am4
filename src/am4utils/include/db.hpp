#include <duckdb.hpp>
#include <vector>

using namespace std;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)
#define CHECK_SUCCESS(q) if (q->HasError()) throw DatabaseException(q->GetError());

#ifdef CORE_DIR
static string home_dir = MACRO_STRINGIFY(CORE_DIR);
#else
static string home_dir = "";
#endif

// multiple threads can use the same connection?
// https://github.com/duckdb/duckdb/blob/8c32403411d628a400cc32e5fe73df87eb5aad7d/test/api/test_api.cpp#L142
struct Database {
    duckdb::unique_ptr<duckdb::DuckDB> database;
    duckdb::unique_ptr<duckdb::Connection> connection;
    duckdb::unique_ptr<duckdb::PreparedStatement> get_airport_by_id;
    duckdb::unique_ptr<duckdb::PreparedStatement> get_route_demands_by_id;
    
    static shared_ptr<Database> default_client;
    static shared_ptr<Database> Client();
    static shared_ptr<Database> CreateClient();

    void prepare_db();
    void prepare_statements();
};

void init();
void _debug_query(string query);

class DatabaseException : public exception {
private:
    string msg;
public:
    DatabaseException(string msg) : msg(msg) {}
    const char* what() const throw() { return msg.c_str(); }
};