import csv

# for i in range(3983):
with open("data/dist/1.csv", "r", encoding='utf-8-sig', newline='') as f:
    data = list(csv.reader(f))
    for d in data:
        d = d[:4]
        print(d)