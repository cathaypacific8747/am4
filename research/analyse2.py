import pandas as pd
from scipy.optimize import minimize
import numpy as np

maxtarget = 50
target = [i for i in range(0, maxtarget)]
demandtable = np.zeros((maxtarget, maxtarget), dtype=int)

odf = pd.read_csv('airports.csv', delimiter=';')

guess = []
for oid in target:
    try:
        guess.append(0.0015675738*float(odf[odf.id == oid].price) - 10.8522121330)
    except:
        guess.append(0)
    try:
        df = pd.read_csv(f'demands/{oid}.csv', delimiter=',', names=['destid', 'yd', 'jd', 'fd', 'destname', 'destcountry', 'iata', 'icao', 'runway', 'distance']).dropna()
        for row in df.itertuples():
            did = row.destid
            if did > oid and did in target:
                demandtable[oid, did] = int(row.yd)
                # print(f"{oid} -> {did}: {row.yd} {row.jd} {row.fd}, {z[oid, did]}")
    except Exception:
        pass

# implement backpropagation

def errorfunc(params):
    error = 0
    for oid_idx in range(len(params)):
        for did_idx in range(len(params)):
            if oid_idx >= did_idx:
                continue
            res = demandtable[oid_idx, did_idx]
            if res == 0:
                continue
            error += abs(res - (params[oid_idx] + params[did_idx]))
    return error

# minimise for cost function
# guess = np.zeros((maxtarget), dtype=np.float32)
# guess = np.full((maxtarget), 200, dtype=np.float64)
res = minimize(errorfunc, guess, bounds=[(0, 1500) for _ in range(maxtarget)], method='SLSQP')
for row in res.x:
    print(row)