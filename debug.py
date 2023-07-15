import am4utils
from am4utils.aircraft import Aircraft
from am4utils.airport import Airport
from am4utils.route import Route

if __name__ == '__main__':
    print(f'py: am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]}')
    am4utils.db.init()

    # ac = Aircraft.search('b744').ac
    # print(ac)
    ap = Airport.search('iata:IPC').ap
    print(ap)

    ap0 = Airport.search('LPB').ap
    ap1 = Airport.search('CNF').ap
    ac = Aircraft.search('erj192').ac
    # print(ac)
    r = Route.create(ap0, ap1).assign(ac)
    cfg = r.aircraft.config.pax_config
    # print(cfg.y, cfg.j, cfg.f, cfg.algorithm)
    print(r.route.direct_distance)
    print(r.ticket.pax_ticket.y)
    print(r.ticket.pax_ticket.j)
    print(r.ticket.pax_ticket.f)
    # print(r.income)