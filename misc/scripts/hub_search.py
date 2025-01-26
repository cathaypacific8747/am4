# %%
import csv
import os
import time

from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.db import init
from am4.utils.game import User
from am4.utils.route import AircraftRoute, Destination, RoutesSearch
from tqdm import tqdm

init()


def all_airports():
    for i in range(3984):
        apsr = Airport.search(f"id:{i}")
        if apsr.ap.valid:
            yield apsr.ap


# %%
ac = Aircraft.search("a388[s,f,c]")
# ac = Aircraft.search('an225[s,f,c]')
options = AircraftRoute.Options(
    max_distance=6000,
    # max_distance=8000,
    tpd_mode=AircraftRoute.Options.TPDMode.STRICT_ALLOW_MULTIPLE_AC,
    trips_per_day_per_ac=5,
)
user = User.Default()
user.wear_training = 5
user.repair_training = 5
user.l_training = 6
user.h_training = 6
user.fuel_training = 3
user.co2_training = 3
user.load = 0.9
user.cargo_load = 0.9
user.income_loss_tol = 0.9
# %%
start = time.time()
all_dest = {}
for ap in tqdm(list(all_airports())):
    rs = RoutesSearch(ap, ac.ac, options, user)
    all_dest[ap] = rs.get()
print(f"took {time.time() - start}s")

# %%
results = {}
for ap, dests in all_dest.items():
    if len(dests) < 1:
        continue
    count = 0
    score = 0
    income = 0
    with open(f"data/a388/{ap.icao}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "dest.icao",
                "dest.name",
                "dest.country",
                "yd",
                "jd",
                "fd",
                "dist",
                "trips_per_day_per_ac",
                "yc",
                "jc",
                "fc",
                "yt",
                "jt",
                "ft",
                "income",
            ]
        )
        for d in dests:
            d: Destination
            if d.ac_route.route.direct_distance > 5500:
                count += 1
                score += d.ac_route.trips_per_day_per_ac * d.ac_route.route.direct_distance
                income += d.ac_route.trips_per_day_per_ac * d.ac_route.profit
                acr: AircraftRoute = d.ac_route
                writer.writerow(
                    [
                        d.airport.icao,
                        d.airport.name,
                        d.airport.country,
                        acr.route.pax_demand.y,
                        acr.route.pax_demand.j,
                        acr.route.pax_demand.f,
                        acr.route.direct_distance,
                        acr.trips_per_day_per_ac,
                        acr.config.y,
                        acr.config.j,
                        acr.config.f,
                        acr.ticket.y,
                        acr.ticket.j,
                        acr.ticket.f,
                        acr.income,
                    ]
                )
    results[ap] = (count, score, income)
# %%
for ap, (count, score, income) in sorted(results.items(), key=lambda x: x[1][1], reverse=True):
    ap: Airport
    print(f"{count} | {score:.0f} | ${income/1e6:>4.0f}M | {ap.icao} | {ap.name}, {ap.country}")
    if count > 10:
        os.system(f"cp data/a388/{ap.icao}.csv data/{ap.icao}.csv")
# %%
