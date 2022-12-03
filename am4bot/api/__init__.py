import os
import csv
import rich
import time
# import lzma
# from io import StringIO
import pandas as pd
import pyarrow.feather as feather

from api.route import Route

from .aircraft import Aircraft
from .airport import Airport

class API:
    def __init__(self):
        self._success('started api')
        # self.__set_aircrafts()
        # self.__set_airports()
        self.__set_routes()

    def _success(self, text):
        rich.print(f'[green]{time.time()} INFO: {text}[/]')

    def _path(self, *path) -> str:
        return os.path.join(os.path.dirname(__file__), *path)

    def __set_aircrafts(self):
        with open(self._path('data', 'aircrafts.csv'), 'r') as f:
            self.aircrafts = tuple(Aircraft(*r) for r in csv.reader(f))
        
        self.aircraft_shortname_hashtable = {}
        for i, a in enumerate(self.aircrafts):
            self.aircraft_shortname_hashtable[a.a_shortname] = i

    def __set_airports(self):
        with open(self._path('data', 'airports.csv'), 'r') as f:
            self.airports = tuple(Airport(*r) for r in csv.reader(f))
            self._success('finished loading airports!')

        self.airport_icao_hashtable = {}
        self.airport_iata_hashtable = {}
        self.airport_id_hashtable = {}
        for i, a in enumerate(self.airports):
            self.airport_icao_hashtable[a.icao] = i
            self.airport_iata_hashtable[a.iata] = i
            self.airport_id_hashtable[a.id] = i

    def __set_routes(self):
        start = time.perf_counter()
        df = pd.read_csv(self._path('data', 'routes.csv'), sep=',', header=0, index_col=0)
        i = df.info(verbose=True, memory_usage='deep')
        print(i)
        # with lzma.open(self._path('data', 'routes'), 'r') as f:
        #     for row in csv.reader(StringIO(f.read().decode('utf-8'))):
        #         oid, did, yd, jd, fd = map(int, row[:-1])
        #         dist = float(row[-1])
        
        # with open(self._path('data', 'routes.csv'), 'r') as f:
        #     for row in csv.reader(f):
        #         oid, did, yd, jd, fd = map(int, row[:-1])
        #         dist = float(row[-1])

        self._success(time.perf_counter() - start)
        self._success('finished loading routes!')

    def get_airport_by_icao(self, icao: str) -> Airport:
        return self.airports[self.airport_icao_hashtable[icao]]
    
    def get_airport_by_iata(self, iata: str) -> Airport:
        return self.airports[self.airport_iata_hashtable[iata]]
    
    def get_airport_by_id(self, id: int) -> Airport:
        return self.airports[self.airport_id_hashtable[id]]