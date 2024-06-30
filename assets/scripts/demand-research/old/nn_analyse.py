import pandas as pd
import numpy as np
import pyarrow.feather as pfeather
# import pyarrow.compute as pc
# import pyarrow.csv as pcsv
# import pyarrow as pa
# import duckdb
import matplotlib.pyplot as plt

# high distrib: 48000, 60000, 6000
# 1101: 60k
# 1939: 42k
apdf = pd.read_csv('airports.csv', delimiter=',', index_col='id')
hub_cost = {}
for row in apdf.itertuples():
    hub_cost[row.Index] = row.hub_cost

dems = {}
aspdf = pd.read_csv('airports_shrunk.csv', delimiter=',', index_col='id')
for id, _icao, _hc, done, yd, jd, fd in aspdf.itertuples():
    if not done or not yd > 1:
        continue
    dems[id] = (yd, jd, fd)

routes_feather = pfeather.read_table('routes').to_pandas()
# con = duckdb.connect(':memory:')
# con.register('routes', routes_feather)

A = np.zeros((3983, 3983), dtype=np.float32)
for oid, did, yd, jd, fd, d in routes_feather.itertuples(index=False):
    # v = (hub_cost[oid] + hub_cost[did]) / (yd + jd + fd)
    # v = yd / (hub_cost[oid] + hub_cost[did])
    v = yd
    A[oid][did] = v
    A[did][oid] = v

A.sort(axis=1)
## 2D
# A.sort(axis=0)
# plt.matshow(A, cmap='turbo')
# plt.savefig('routes_matrix4.png', dpi=600)
# plt.show()


## 3D
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# x, y = np.meshgrid(np.arange(0, 3983, 1), np.arange(0, 3983, 1))
# ax.plot_surface(x, y, A, cmap='turbo')
# plt.savefig('routes_matrix3.png', dpi=600)
# plt.show()

# plot on line graph
# l = []
# for i in range(3983):
#     plt.plot(A[i], alpha=.05)
#     l.append((i, np.sum(A[i])))

# l.sort(key=lambda x: x[1])
# print(l)

# plt.savefig('routes_graph.png', dpi=600)
# plt.show()

xs, ys = [], []
for id, dem in dems.items():
    yd, jd, fd = dem
    avg = np.average(A[id])
    xs.append(avg)
    ys.append(yd)

plt.scatter(xs, ys)
plt.savefig('routes_graph2.png', dpi=600)
plt.show()