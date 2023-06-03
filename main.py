import am4utils

# if __name__ == '__main__':
#     for s in dir(am4utils):
#         print(s, am4utils.__dict__[s])
#     print('___')
#     test()
#     print('TESTS COMPLETED')

print(f'py: am4utils ({am4utils._core.__version__}), coredir {am4utils._core.__coredir__}')
success = am4utils.db.init()

# ticket = am4utils.route.create_optimal_pax_ticket(10000, am4utils.GameMode.EASY) # 4580 9240 13990
# help(ticket)

ap0 = am4utils.airport.from_id(1)
ap1 = am4utils.airport.from_id(2)
r = am4utils.route.from_airports(ap0, ap1)
print(r)