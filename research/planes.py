import csv
import json
import os

rows = []
for l in os.listdir('planes'):
    with open(os.path.join('planes', l), 'r') as f:
        for aircraft in json.load(f):
            a_name = aircraft['name']
            price = aircraft['price']
            speed = aircraft['speed']
            range = aircraft['range']
            rwy = aircraft['runway']
            capacity = aircraft['capacity']
            type = aircraft['type']
            picture = aircraft['picture']
            manufacturer = aircraft['manufacturer']
            fuel = aircraft['fuel']
            co2 = aircraft['co2']
            ac = aircraft['A_check']
            acheck_price, acheck_time = ac['price'], ac['time']
            st = aircraft['staff']
            pilots, crew, engineers, tech = st['pilots'], st['crew'], st['engineers'], st['tech']
            for e in aircraft['engines']:
                e_name, fuel, speed = e['name'], e['fuel'], e['speed']

                rows.append[[manufacturer, a_name, price, speed, range, rwy, capacity, type, picture,]]
                rows.append([a_name, price, speed, range, rwy, capacity, type, picture,
                manufacturer, fuel, co2, acheck_price, acheck_time, pilots, crew, engineers, tech,
                e_name, fuel, speed])

with open('planes.csv', 'w+') as f:
    writer = csv.writer(f)
    writer.writerows(rows)