import torch
import torch.nn as nn
import torch.optim as optim
# import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import time
import matplotlib.pyplot as plt

torch.manual_seed(3)
plt.style.use('dark_background')

# airports = [
#     (23, 25),
#     (10, 13),
#     (5, 8),
#     (40, 22),
#     (17, 27),
#     (12, 16),
#     (9, 49),
#     (31, 3),
#     (49, 23),
#     (21, 14),
# ]
airports = torch.randint(10, 50, (200, 2))
N = len(airports)

# for i in range(N):
#     for j in range(N):
#         ai, bi = airports[i]
#         aj, bj = airports[j]
#         demand = ai*aj + bi*bj if i != j else ''
#         print(f'{demand:>4}', end=' ' if j < N-1 else '\n')

'''
  x   555  315 1470 1066  676 1432  788 1702  833
 555   x   154  686  521  328  727  349  789  392
 315  154   x   376  301  188  437  179  429  217
1470  686  376   x  1274  832 1438 1306 2466 1148
1066  521  301 1274   x   636 1476  608 1454  735
 676  328  188  832  636   x   892  420  956  476
1432  727  437 1438 1476  892   x   426 1568  875
 788  349  179 1306  608  420  426   x  1588  693
1702  789  429 2466 1454  956 1568 1588   x  1351
 833  392  217 1148  735  476  875  693 1351   x 
'''

class DemandModel(nn.Module):
    def __init__(self):
        super(DemandModel, self).__init__()
        self.A = nn.Parameter(torch.rand(N) * 50)
        self.B = nn.Parameter(torch.rand(N) * 50)
        # self.A = nn.Parameter(torch.tensor([24.271718978881836, 11.286245346069336, 6.19169807434082, 34.66632080078125, 20.755327224731445, 13.712613105773926, 29.03990936279297, 28.005725860595703, 19.142927169799805, 18.854366302490234], requires_grad=True))
        # self.B = nn.Parameter(torch.tensor([24.794269561767578, 11.972960472106934, 6.876227855682373, 29.27152442932129, 23.247785568237305, 14.5870943069458, 20.36739730834961, 5.607189178466797, 50.246864318847656, 17.350332260131836], requires_grad=True))

    def forward(self, I):
        I0, I1 = I[:, 0], I[:, 1]
        return torch.sum(I0 * self.A, dim=1) * torch.sum(I1 * self.B, dim=1) + torch.sum(I0 * self.B, dim=1) * torch.sum(I1 * self.A, dim=1)

n = DemandModel()
# I0 = torch.zeros(1, N); I0[0][0] = 1
# I1 = torch.zeros(1, N); I1[0][1] = 1
# result = n(I0, I1)
# print(result)

criterion = nn.MSELoss()
optimizer = optim.Adam(n.parameters(), lr=.05)

xs = []
ys = []
for i in range(N):
    for j in range(N):
        I = torch.zeros(2, N, dtype=torch.bool)
        if i == j:
            continue
        I[0][i] = True
        I[1][j] = True
        ai, bi = airports[i]
        aj, bj = airports[j]
        D = (ai*aj + bi*bj).float()
        # D = torch.tensor(ai*aj + bi*bj, dtype=torch.float32)
        xs.append(I)
        ys.append(D)

dataset = TensorDataset(torch.stack(xs), torch.stack(ys))
dataloader = DataLoader(
    dataset,
    # batch_size=N*(N-1),
    batch_size=N-1,
    shuffle=True
)

print('start')
start = time.time()

best = (float('inf'), None, None)
results = []
for _ in range(500):
    for bxs, bys in dataloader:
        optimizer.zero_grad()
        yhat = n(bxs)
        loss = criterion(yhat, bys)
        loss.backward()
        optimizer.step()
    
    l = torch.sqrt(loss)
    print(f"Loss: {l}")
    # print([f'{v:.1f}' for v in n.A.tolist()])
    # print([f'{v:.1f}' for v in n.B.tolist()])
    if l < best[0]:
        best = (l, [v for v in n.A.tolist()], [v for v in n.B.tolist()])
    results.append(float(l))

A = best[1]
B = best[2]
print(f'________predicted')
print(f'Loss: {best[0]}')
print(A)
print(B)
print(f'time taken: {time.time() - start}')

print('________true')
Ao = airports[:, 0]
Bo = airports[:, 1]
print(Ao)
print(Bo)

plt.plot(results)
plt.show()

# for i in range(N):
#     for j in range(N):
#         ai, bi = A[i], B[i]
#         aj, bj = A[j], B[j]
#         demand = int(ai*aj + bi*bj) if i != j else ''
#         print(f'{demand:>4}', end=' ' if j < N-1 else '\n')


# for i in range(N):
#     for j in range(N):
#         ai, bi = airports[i]
#         aj, bj = airports[j]
#         demand = ai*aj + bi*bj if i != j else ''
#         print(f'{demand:>4}', end=' ' if j < N-1 else '\n')

