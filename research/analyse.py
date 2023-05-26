#%%
import pandas as pd
import numpy as np
import pyarrow.feather as pfeather
import matplotlib.pyplot as plt

# 1101: 60k
# 1939: 42k
apdf = pd.read_csv('airports.csv', delimiter=',', index_col='id')
# extract columns id and hub_cost
hc = {}
for row in apdf.itertuples():
    hc[row.Index] = row.hub_cost

routes_feather = pfeather.read_table('routes').to_pandas()

#%%
A = np.zeros((3983, 3983), dtype=np.int16)
for oid, did, yd, jd, fd, d in routes_feather.itertuples(index=False):
    v = (hc[oid] + hc[did]) / (yd + jd + fd)
    A[oid][did] = v
    # A[did][oid] = v

# reorder the columns of matrix such that the most expensive airports are at the top
A = A[:, A.sum(axis=0).argsort()[::-1]]
plt.matshow(A, cmap='turbo')
plt.show()
plt.savefig('routes_matrix.png', dpi=600)

#%%
i = 0

xs, ys = [], []
xs1, ys1 = [], []
xs2, ys2 = [], []
for oid, did, yd, jd, fd, d in routes_feather.itertuples(index=False):
    hc0, hc1 = hc[oid], hc[did]
    if hc0 != 48000 or hc1 != 48000:
        continue

    if hc0 >= 189600 and hc1 >= 189600:
        xs2.append(hc0 + hc1)
        ys2.append(yd)
    elif hc0 >= 189600 or hc1 >= 189600:
        xs1.append(hc0 + hc1)
        ys1.append(yd)
    else:
        xs.append(hc0 + hc1)
        ys.append(yd)
    
    if i % 5000 == 0:
        print(i)
    # if i > 100000:
    #     break
    i += 1

plt.clf()
plt.scatter(xs, ys, color='black', alpha=.1)
plt.scatter(xs1, ys1, color='blue', alpha=.1)
plt.scatter(xs2, ys2, color='green', alpha=.1)
plt.show()
# %%
cnts = {}
for c in hc.values():
    if c not in cnts:
        cnts[c] = 0
    cnts[c] += 1
cnts

#   6000: 664
#  12000: 108
#  23700: 1
#  24000: 151
#  18000: 72
#  30000: 118
#  36000: 235
#  42000: 210
#  48000: 939
#  54000: 386
#  60000: 766
# 189600: 1
# 213300: 117
# 237000: 139
# %%
