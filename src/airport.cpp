#include <duckdb.hpp>
#include "airport.hpp"

using namespace duckdb;
using namespace std;

int get_airport_by_id(int id)
{
    DuckDB db(nullptr);
    Connection con(db);

	con.Query("CREATE TABLE integers(i INTEGER)");
	con.Query("INSERT INTO integers VALUES (3)");
	auto result = con.Query("SELECT * FROM integers");
	result->Print();

    return id;
}