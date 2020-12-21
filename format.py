import csv

filtered = [['id', 'id_departure', 'id_arrival', 'economic_demand', 'business_demand', 'firstClass_demand', 'distance']]
for i in range(1,3983): # 3983
    with open(f'data/dist/{i}.csv', mode='r+') as f:
        data = list(csv.reader(f))
        for d in data:
            if i < int(d[0]) and int(d[1]) != 0 and int(d[2]) != 0 and int(d[3]) != 0:
                filtered.append([f'{i}.{d[0]}', i, d[0], d[1], d[2], d[3], d[4]])
        print(i)

with open(f'master.csv', mode='r+') as f:
    writer = csv.writer(f)
    writer.writerows(filtered)