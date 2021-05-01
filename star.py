import csv
import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='CRITICAL', milliseconds=True) # info
logger.info("Started.")

logger.info("Loaded discord.py.")

# standard modules
import os; os.system("python3 setup.py build_ext --inplace")
from helper_cy import *

# todo: change to perfect hash function for text='HKG', text='VHHH'.
#       add reputation to paxConf and cargoConf

try:
    entries = []
    hubs = ['ASB', 'RAI', 'KRT', 'BAH', 'SIN', 'KUL', 'WLG', 'ASU', 'CGK', 'XCH', 'LIM', 'WLS', 'ADD']
    # hubs = ['BKK', 'DEL', 'DXB', 'FRA', 'GRU', 'IXE', 'JFK', 'LHR', 'ORD', 'PEK', 'SYD']

    for h in hubs:
        origAirport = Airport(text=h)
        for k in range(1, 3983):
            destAirport = Airport(apid=k)
            if destAirport.details['valid']:
                r = Route(origAirport, destAirport)
                r.getStopover_contribPriority_raw(targetDist=6000, maxRange=14815, rwyReq=0)
                if r.stopover['success'] and r.flyingDistance == 6000:
                    print(f'{h}:{k}')

                    newSpeed = Speed()
                    newSpeed.from_st(s=r.flyingDistance, t=7.75)
                    c = CI()
                    c.from_vu(v=newSpeed.speed, u=1096*1.1*1.5)
                    r.getContrib_raw(isRealism=False, ci=c.ci)
                    stopAirport = Airport(apid=r.stopover['apid'])

                    r.getDemand_raw(True)
                    fields = (
                        origAirport.details['iata'],
                        origAirport.details['country'],
                        origAirport.details['city'],

                        stopAirport.details['iata'],
                        stopAirport.details['country'],
                        stopAirport.details['city'],

                        destAirport.details['iata'],
                        destAirport.details['country'],
                        destAirport.details['city'],
                        r.distance,
                        r.flyingDistance,

                        r.cargoDemand['l'],
                        r.cargoDemand['h'],
                        '',

                        # r.paxDemand['y'],
                        # r.paxDemand['j'],
                        # r.paxDemand['f'],

                        c.ci,
                        r.contribution
                    )
                    entries.append(fields)
        print(f'{h} done.')
    with open('out.csv', 'w+', encoding='utf-8-sig', newline='') as f:
        wri = csv.writer(f)
        wri.writerows(entries)
except Exception as e:
    print(e)
finally:
    db.close()
    print('MySQL connection closed.')
# origAirport = h