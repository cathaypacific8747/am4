import am4utils

if __name__ == '__main__':
    print(f'py: am4utils ({am4utils._core.__version__}), coredir {am4utils._core.__coredir__}')
    # for s in dir(am4utils):
    #     print(s, am4utils.__dict__[s])

    am4utils.db.init()

    # ticket = am4utils.route.create_optimal_pax_ticket(10000, am4utils.GameMode.EASY) # 4580 9240 13990
    # help(ticket)