import am4utils

print('VERSION', am4utils._core.__version__)
# print('DUCKDB TEST', am4utils.get_airport_by_id(1))
am4utils.init_db()
am4utils.query_db("SELECT * FROM airports;")
# am4utils.query_db("CREATE TABLE testing (id INTEGER);")
# am4utils.query_db("INSERT INTO testing VALUES (1);")
# am4utils.query_db("INSERT INTO testing VALUES (2);")
# am4utils.query_db("COPY testing TO 'testing777777.csv' (DELIMITER ',');")