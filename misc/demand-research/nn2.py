import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import math
import numpy as np
import time
import json


torch.cuda.set_device(0)
torch.manual_seed(3)
plt.style.use('dark_background')
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.rainbow(np.linspace(0, 1, 5)))

N = 4000
A, B = torch.randint(10, 50, (2, N), dtype=torch.float32)
D = A.unsqueeze(1) * B + A * B.unsqueeze(1) # A^T ⊙ B + A ⊙ B^T

xs, ys = [], []
for i in range(N):
    for j in range(N):
        if i == j:
            continue
        xs.append(torch.tensor((i, j)))
        ys.append(D[i][j])

xs = torch.stack(xs)
ys = torch.stack(ys)


class DemandModel(nn.Module):
    def __init__(self):
        super(DemandModel, self).__init__()
        self.A = nn.Parameter(torch.rand(N) * 50)
        self.B = nn.Parameter(torch.rand(N) * 50)
        # self.A = nn.Parameter(A)
        # self.B = nn.Parameter(B)

    def forward(self, batch):
        i, j = batch[:, 0], batch[:, 1]
        # print("----")
        # print(batch)
        # print(self.A)
        # print(self.B)
        # print('****')
        # print(self.A[i])
        # print(self.B[j])
        # print(self.A[j])
        # print(self.B[i])
        # print('[[[[]]]]')
        # print(self.A[i] * self.B[j])
        # print(self.A[j] * self.B[i])
        # print(self.A[i] * self.B[j] + self.A[j] * self.B[i])
        return self.A[i] * self.B[j] + self.A[j] * self.B[i]

# model = torch.compile(DemandModel())
model = DemandModel()

def run(batch_size=N-1, lr=0.01, epochs=1000):
    print(f'*** STARTING: {batch_size=}, {lr=}, {epochs=}')

    # batch = torch.randint(0, 10, (5, 2))
    # out = model(batch)

    # print(batch)
    # print(model.A)
    # print(model.B)
    # print(out)

    optimizer = optim.Adam(model.parameters(), lr=lr)
    # scheduler = StepLR(optimizer, step_size=4, gamma=0.7)
    criterion = nn.MSELoss()

    dataloader = DataLoader(
        TensorDataset(xs, ys),
        batch_size=batch_size,
        shuffle=True
    )

    start = time.time()
    losses = []
    last_model = model
    for e in range(epochs):
        total_loss = 0
        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()
            y_pred = model(batch_x)
            loss = criterion(y_pred, batch_y)
            loss.backward()
            optimizer.step()
            # scheduler.step()
            total_loss += loss.item()
        
        loss = math.sqrt(total_loss / len(dataloader))
        print(f'{e:>5} | {loss=}')

        with open(f'./model/{e}.json', 'w') as f:
            json.dump({
                'A': model.A.tolist(),
                'B': model.B.tolist(),
            }, f)

        if loss < 5e-4:
            print(f'*** PAST CRITERON: {loss=}')
            last_model = model
            break
        if loss < 1 and loss > losses[-1]:
            print(f'*** INCREASING: {loss=}')
            break
        losses.append(loss)
        last_model = model
    
    print(f'*** DONE: {time.time() - start:.2f}s')
    # print(last_model.A)
    # print(last_model.B)
    D_pred = torch.mul(last_model.A.unsqueeze(1), last_model.B) + torch.mul(last_model.A, last_model.B.unsqueeze(1))
    print(D - D_pred)
    print(torch.sum(torch.abs(D - D_pred)))
    
    # evaluate
    

    plt.plot(losses, label=f'{batch_size=}, {lr=}')

# 1000: 0.08: overshot!
# run(batch_size=N//2, lr=0.08, epochs=200)
run(batch_size=N//2, lr=0.04, epochs=200)

# print('________true')
# print(A)
# print(B)

plt.legend()
plt.xlabel('Epoch')
plt.ylabel('MSE Loss')
plt.show()

# n = DemandModel()
# # I0 = torch.zeros(1, N); I0[0][0] = 1
# # I1 = torch.zeros(1, N); I1[0][1] = 1
# # result = n(I0, I1)
# # print(result)

# criterion = nn.MSELoss()
# optimizer = optim.Adam(n.parameters(), lr=.05)

# xs = []
# ys = []
# for i in range(N):
#     for j in range(N):
#         I = torch.zeros(2, N, dtype=torch.bool)
#         if i == j:
#             continue
#         I[0][i] = True
#         I[1][j] = True
#         ai, bi = airports[i]
#         aj, bj = airports[j]
#         D = (ai*aj + bi*bj).float()
#         # D = torch.tensor(ai*aj + bi*bj, dtype=torch.float32)
#         xs.append(I)
#         ys.append(D)

# dataset = TensorDataset(torch.stack(xs), torch.stack(ys))
# dataloader = DataLoader(
#     dataset,
#     # batch_size=N*(N-1),
#     batch_size=N-1,
#     shuffle=True
# )

# print('start')
# start = time.time()

# best = (float('inf'), None, None)
# results = []
# for _ in range(500):
#     for bxs, bys in dataloader:
#         optimizer.zero_grad()
#         yhat = n(bxs)
#         loss = criterion(yhat, bys)
#         loss.backward()
#         optimizer.step()
    
#     l = torch.sqrt(loss)
#     print(f"Loss: {l}")
#     # print([f'{v:.1f}' for v in n.A.tolist()])
#     # print([f'{v:.1f}' for v in n.B.tolist()])
#     if l < best[0]:
#         best = (l, [v for v in n.A.tolist()], [v for v in n.B.tolist()])
#     results.append(float(l))

# A = best[1]
# B = best[2]
# print(f'________predicted')
# print(f'Loss: {best[0]}')
# print(A)
# print(B)
# print(f'time taken: {time.time() - start}')

# print('________true')
# Ao = airports[:, 0]
# Bo = airports[:, 1]
# print(Ao)
# print(Bo)

# plt.plot(results)
# plt.show()
