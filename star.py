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
    origAirport = Airport(apid=2394)
    for k in range(1, 3983):
        destAirport = Airport(apid=k)
        if destAirport.details['valid']:
            r = Route(origAirport, destAirport)
            r.getStopover_contribPriority_raw(targetDist=6000, maxRange=5500, rwyReq=0)
            if r.stopover['success']:
                r.getTickets_raw(isCargo=False, isRealism=False)
                stopAirport = Airport(apid=r.stopover['apid'])

                fields = [
                    origAirport.details['city'],
                    origAirport.details['country'],
                    stopAirport.details['city'],
                    stopAirport.details['country'],
                    destAirport.details['city'],
                    destAirport.details['country']
                ]

                # entries.append({
                #     'oName': f"{origAirport.details['city']}, {origAirport.details['country']}",
                #     'oIata': origAirport.details['iata'],
                #     'o': origAirport,
                #     'sName': f"{stopAirport.details['city']}, {stopAirport.details['country']}",
                #     'sIata': stopAirport.details['iata'],
                #     's': stopAirport,
                #     'dName': f"{destAirport.details['city']}, {destAirport.details['country']}",
                #     'dIata': destAirport.details['iata'],
                #     'd': destAirport,
                # })
    ci = CI()
    ci.from_vu(700, 1049)
    print(ci.ci)
except Exception as e:
    print(e)
finally:
    db.close()
    print('MySQL connection closed.')
# origAirport = h