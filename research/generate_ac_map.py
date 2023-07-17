# generates id -> idx map.

import csv

d = {}
with open('web/aircrafts.new.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for i, row in enumerate(reader):
        apid = int(row[0])
        if apid not in d:
            d[apid] = i

for apid, i in d.items():
    print(f"{{{apid}, {i}}}, ", end='')
print()