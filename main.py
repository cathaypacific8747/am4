import am4utils

# def test():
#     ey0 = am4utils.optimal_y_easy_price(10000)
#     e = am4utils.create_pax_ticket(10000, True)
#     assert ey0 == e.y_price == 4580

# if __name__ == '__main__':
#     for s in dir(am4utils):
#         print(s, am4utils.__dict__[s])
#     print('___')
#     test()
#     print('TESTS COMPLETED')

print('VERSION', am4utils._core.__version__)
print('COREDIR', am4utils._core.__coredir__)
am4utils.db.init()
am4utils.db._query("SELECT * FROM airports WHERE id=1;")