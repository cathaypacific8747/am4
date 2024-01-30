#%%
import time

from am4utils.aircraft import Aircraft
from am4utils.airport import Airport
from am4utils.db import init
from am4utils.game import User
from am4utils.route import AircraftRoute, Destination, find_routes
from tqdm import tqdm

init(db_name='debug')

def all_airports():
    for i in range(3984):
        apsr = Airport.search(f"id:{i}")
        if apsr.ap.valid:
            yield apsr.ap

#%%
ac = Aircraft.search('a388[s,f,c]')
# ac = Aircraft.search('an225[s,f,c]')
options = AircraftRoute.Options(
    max_distance=6000,
    # max_distance=8000
)
user = User.Default()
user.wear_training = 5
user.repair_training = 5
user.l_training = 6
user.h_training = 6
user.fuel_training = 3
user.co2_training = 3
user.load = 0.94
# user.load = 0.9
user.income_loss_tol = 0.9
#%%
start = time.time()
all_dest = {}
for ap in tqdm(list(all_airports())):
    destinations = find_routes(
        ap,
        ac.ac,
        options,
        user
    )
    all_dest[ap] = destinations
print(f"took {time.time() - start}s")

# %%
results = {}
for ap, dests in all_dest.items():
    if len(dests) < 1:
        continue
    count = 0
    score = 0
    income = 0
    for d in dests:
        d: Destination
        if d.ac_route.route.direct_distance > 5500:
            count += 1
            score += d.ac_route.trips_per_day * d.ac_route.route.direct_distance
            income += d.ac_route.trips_per_day * d.ac_route.profit
            # print(d.airport.icao, d.ac_route.route.direct_distance, d.ac_route.income, d.ac_route.trips_per_day)
    results[ap] = (count, score, income)
# %%
for ap, (count, score, income) in sorted(results.items(), key=lambda x: x[1][1], reverse=True):
    ap: Airport
    print(f"{count} | {score:.0f} | ${income/1e6:>4.0f}M | {ap.icao} | {ap.name}, {ap.country}")
# %%
