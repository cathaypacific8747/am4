import am4utils

print('VERSION', am4utils.__version__)
print('OPTIMAL Y PRICE', am4utils.optimal_y_easy_price(10000))
print('DUCKDB TEST', am4utils.get_airport_by_id(1))