#%%
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import math
import numpy as np
import time
import json
import os
if not os.path.exists('models'):
    os.mkdir('models')

torch.manual_seed(3)
plt.style.use('dark_background')
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.rainbow(np.linspace(0, 1, 5)))
#%%
# import csv

# A, B = torch.zeros(2, 3983, dtype=torch.float32)
# D = torch.zeros(3983, 3983, dtype=torch.float32)
# a = dict()
# with open('routes.csv', 'r') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         oid = int(row[0])
#         did = int(row[1])
#         yd = int(row[2])

#         D[oid][did] = yd
#         D[did][oid] = yd
#         a.setdefault(oid, []).append(yd)
#         a.setdefault(did, []).append(yd)

# for i, v in a.items():
#     est_ab = (sum(v) / len(v) / 2) ** .5
#     A[i] = est_ab
#     B[i] = est_ab

# torch.save(A, 'models/A.pt')
# torch.save(B, 'models/B.pt')
# torch.save(D, 'models/D.pt')

#%%
# capital_ids = [3254, 3320, 935, 2643, 2115, 563, 3264, 716, 632, 2321, 3253, 3564, 3731, 559, 833, 2113, 1074, 2313, 3, 3228, 3239, 1261, 1760, 3031, 3256, 1087, 3064, 1098, 810, 2006, 3250, 1035, 681, 961, 2012, 2121, 1780, 2492, 1023, 356, 2245, 2320, 1440, 1304, 2317, 3451, 3939, 3841, 2541, 1004, 2315, 1084, 599, 1052, 3207, 2504, 1401, 1996, 3862, 440, 1223, 791, 3235, 811, 618, 2149, 3533, 981, 970, 1914, 2644, 501, 2687, 806, 3536, 3721, 3349, 426, 3242, 1583, 3688, 934, 3080, 3240, 3904, 3911, 455, 2318, 184, 2774, 996, 3263, 740, 442, 923, 1658, 3574, 555, 610, 3276, 3388, 1561, 3571, 1399, 807, 2259, 2309, 573, 388, 2763, 3268, 3568, 389, 2494, 2499, 2218, 3950, 973, 1999, 2406, 921, 3289, 1011, 1047, 796, 2495, 3857, 25, 3070, 2401, 3890, 867, 2029, 645, 735, 36, 18, 983, 834, 2107, 3400, 2047, 1502, 3234, 32, 2306, 2312, 3271, 1008, 2947, 3393, 3647, 2663, 2552, 2490, 3870, 3258, 2917, 2304, 2249, 2394, 496, 909, 305, 3146, 2135, 2057, 3305, 3293, 2062, 956, 897, 1762, 971, 3925, 1136, 2072, 2669, 2035, 1661, 1082, 1771, 3620, 2190, 2793, 2040, 3069, 2361, 396, 1028, 3532, 2424, 3147, 1912, 3155, 889, 460, 1877, 3512, 3948, 3246, 1486, 3181, 2350, 629, 1070, 2534, 3729, 2513, 892, 3917, 2850, 1438, 3232, 830, 3425, 1027, 825, 1427, 432, 3499, 2238, 2111, 2146, 3135, 3231, 3696, 3404, 3500, 3237, 2109, 465, 2301, 3461, 799, 3262, 3934, 2132, 2545, 1938, 3868, 419, 2276, 905, 1756, 2457, 836, 822, 3236, 1259, 1001, 914, 1, 1982, 3963, 1791, 2493, 3982]
# torch.save(torch.tensor(capital_ids), 'models/capital_ids.pt')

#%%

As = torch.load('./models/As_V1.pt').cpu()
Bs = torch.load('./models/Bs_V1.pt').cpu()
capital_ids = torch.load('./models/capital_ids.pt').cpu()

class DemandModel(nn.Module):
    def __init__(self):
        super(DemandModel, self).__init__()
        self.As = nn.Parameter(As)
        self.Bs = nn.Parameter(Bs)

    def forward(self, batch): # [[a, b], [c, d]], OD pairs
        row_idxs = torch.any(torch.isin(batch, capital_ids), dim=1).long()
        # [any(a in cid, b in cid), any(c in cid, d in did)].int() -> [1, 0]
        A = self.As[row_idxs]
        B = self.Bs[row_idxs]
        
        i, j = batch.t().unsqueeze(2) # i: [[i0], [i1], ...]
        Ai = A.gather(1, i)
        Aj = A.gather(1, j)
        Bi = B.gather(1, i)
        Bj = B.gather(1, j)
        return (Ai * Aj + Bi + Bj).squeeze(1)

model = DemandModel()
test = torch.tensor([[1, 2]])
model(test)
#%%

N = 3983
# D = torch.load('./models/D.pt', map_location='cuda')
# print('________true')
# print(D)

mask = ~torch.eye(N, dtype=bool)
# ys = D[mask].reshape(-1)

mask = mask.view(-1)
i = torch.arange(N).repeat(N)[mask]
j = torch.arange(N).repeat_interleave(N)[mask]

xs = torch.stack((i, j), dim=1)
D_pred = torch.zeros((N, N), dtype=torch.float32)
#%%
dataloader = DataLoader(
    xs,
    batch_size=3982,
    shuffle=False
)
i = 0
for batch in dataloader:
    D_pred.index_put_(tuple(batch.t()), model(batch))
    if i % 10 == 0:
        print(i)
    i += 1

#%%

# D_pred = A * A.unsqueeze(1) # A ⊙ A
# D_pred.fill_diagonal_(0)
# print(D_pred)
# print('________pred')
# err = D - D_pred
# err_np = err.cpu().detach().numpy()
# err_np.sort(axis=1)
# plt.matshow(err_np, cmap='RdBu')
# plt.savefig('err.png', dpi=600)

#%%

plt.clf()
for i in range(1500):
    plt.plot(err_np[i], color='white', alpha=.2, linewidth=.1)
    if i % 100 == 0:
        print(i)
# plt.gca().set_xscale('symlog')
plt.savefig('err_lines.png', dpi=600)

#%%
err2 = torch.abs(err)
err2_np = err2.cpu().detach().numpy()
# err2_np.sort(axis=1)
# err2_np.sort(axis=0)
plt.matshow(err2_np, cmap='turbo')
plt.savefig('err2.png', dpi=600)

plt.clf()
for i in range(2000):
    plt.plot(err2_np[i], color='white', alpha=.2, linewidth=.1)
    if i % 100 == 0:
        print(i)
# plt.gca().set_xscale('symlog')
plt.savefig('err2_lines.png', dpi=600)

err2_mean = np.mean(err2_np, axis=1)

avg_err2s = []
for i in range(N):
    avg_err2s.append((i, float(err2_mean[i])))

avg_err2s.sort(key=lambda v: v[1], reverse=True)
with open('avg_err2s.csv', 'w') as f:
    for i, m in avg_err2s:
        f.write(f'{i},{m}\n')