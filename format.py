import csv
import math
import os

def distanceCoor(lat1, lon1, lat2, lon2): # radians
    return 12742 * math.asin(math.sqrt(math.pow(math.sin((lat2-lat1) / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin((lon2-lon1) / 2), 2)))

with open("data/ap-indexed-radians.csv", encoding='utf-8', newline='') as f:
    airports = list(csv.reader(f, delimiter=';'))

def getCoordsById(s):
    try:
        return float(airports[s-1][7]), float(airports[s-1][8])
    except:
        return None, None

for origId in range(1002,1003):
    with open(f"data/dist/{origId}.csv", "r", encoding='utf-8-sig', newline='') as f:
        data = list(csv.reader(f))
        dic = dict([[i+1, True] for i in range(1,3983)])
        lst = [[True, i] for i in range(1,3983)]
        
        newData = []
        for d in data:
            try:
                thisId = int(d[0].replace('\ufeff', ''))
                if d[1]:
                    dLat, dLon = getCoordsById(thisId)
                    oLat, oLon = getCoordsById(origId)
                    if oLat and oLon and dLat and dLon:
                        dist = distanceCoor(oLat, oLon, dLat, dLon)
                    else:
                        dist = 0
                    newData.append([thisId, d[1], d[2], d[3], dist])
                else:
                    newData.append([thisId, 0, 0, 0, 0])
                lst[thisId-1][0] = False
            except:
                print(f"{origId} FAILED: {d}")
        
        for l in lst:
            if l[0]:
                # print(l[1])
                newData.append([l[1]+1, 0, 0, 0, 0])
                # lst[l[1]][0] = False

        newData.sort(key=lambda x:x[0])

        with open(f"data/dist1/{origId}.csv", "w", newline='') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(newData)
            
        with open(f"data/dist1/{origId}.csv", "rb+") as f:
            f.seek(-1, os.SEEK_END)
            f.truncate()
    print(f"{origId} done.")