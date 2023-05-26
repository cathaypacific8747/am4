import am4utils

print('VERSION', am4utils.__version__)

def test():
    ey0 = am4utils.optimal_y_easy_price(10000)
    e = am4utils.create_pax_ticket(10000, True)
    assert ey0 == e.y_price == 4580
    print('d=10000, ey_price:', e.y_price)

if __name__ == '__main__':
    test()