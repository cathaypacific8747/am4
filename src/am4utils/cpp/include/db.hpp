#include <duckdb.hpp>
#include <vector>

using std::string;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)
#define CHECK_SUCCESS(q) if (q->HasError()) throw DatabaseException(q->GetError());

// multiple threads can use the same connection?
// https://github.com/duckdb/duckdb/blob/8c32403411d628a400cc32e5fe73df87eb5aad7d/test/api/test_api.cpp#L142
struct Database {
    duckdb::unique_ptr<duckdb::DuckDB> database;
    duckdb::unique_ptr<duckdb::Connection> connection;
    duckdb::unique_ptr<duckdb::PreparedStatement> get_airport_by_id;
    duckdb::unique_ptr<duckdb::PreparedStatement> get_airport_by_iata;
    duckdb::unique_ptr<duckdb::PreparedStatement> get_airport_by_icao;
    duckdb::unique_ptr<duckdb::PreparedStatement> get_airport_by_name;
    duckdb::unique_ptr<duckdb::PreparedStatement> get_airport_by_all;
    duckdb::unique_ptr<duckdb::PreparedStatement> suggest_airport_by_iata;
    duckdb::unique_ptr<duckdb::PreparedStatement> suggest_airport_by_icao;
    duckdb::unique_ptr<duckdb::PreparedStatement> suggest_airport_by_name;

    duckdb::unique_ptr<duckdb::PreparedStatement> get_route_demands_by_id;
    
    static std::shared_ptr<Database> default_client;
    static std::shared_ptr<Database> Client();
    static std::shared_ptr<Database> CreateClient();

    void insert(string home_dir);
    void prepare_statements();
};

void init(string home_dir);
void _debug_query(string query);

class DatabaseException : public std::exception {
private:
    string msg;
public:
    DatabaseException(string msg) : msg(msg) {}
    const char* what() const throw() { return msg.c_str(); }
};