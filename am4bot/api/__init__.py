from loguru import logger
# from rich import inspect, print
import os
import csv
import time
import shutil
# import pandas as pd
import pyarrow as pa
import pyarrow.feather as pa_feather
import pyarrow.csv as pa_csv
import duckdb

from config import Config
from .aircraft import Aircraft
from .airport import Airport
from .route import Route

class API:
    def __init__(self, config: Config):
        logger.debug('initializing API')
        self.config = config
        self.con = duckdb.connect(":memory:")
        self.create_database()

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
            logger.debug('finished loading airports')

        self.airport_icao_hashtable = {}
        self.airport_iata_hashtable = {}
        self.airport_id_hashtable = {}
        for i, a in enumerate(self.airports):
            self.airport_icao_hashtable[a.icao] = i
            self.airport_iata_hashtable[a.iata] = i
            self.airport_id_hashtable[a.id] = i

    def __set_routes(self):
        logger.debug('finished loading routes')

    def __get_sql_statement(self, filename: str) -> str:
        with open(self._path('sql', filename), 'r') as f:
            return f.read()

    def create_database(self):
        logger.debug('start database')
        routes_arrow = pa_feather.read_table(self._path('data', 'routes'))
        self.con.execute("CREATE TABLE routes AS SELECT * FROM routes_arrow")
        self.con.execute("INSERT INTO routes SELECT * FROM routes_arrow")
        
        self.con.register('routes', self.routes_arrow)
        res = self.con.execute("SELECT * FROM routes WHERE yd > 1600 AND d > 17000 ORDER BY (yd+jd*2+fd*3) DESC").df()

        # self.airports_arrow = pa_csv.read_csv(self._path('data', 'airports.csv'))
        # self.con.register('airports', self.airports_arrow)
        # res = self.con.execute("SELECT * FROM airports").df()
        print(res)
        logger.debug('all done')