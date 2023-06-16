import pytest

import am4utils
from am4utils.aircraft import (
    Aircraft,
    PaxConfig, CargoConfig
)
from am4utils.airport import Airport
from am4utils.route import Route

am4utils.db.init(am4utils.__path__[0])

## aircraft tests
@pytest.mark.parametrize("inp", [
    'id:1',
    'shortname:b744',
    'name:B747-400'
])
def test_aircraft_search(inp):
    a0 = Aircraft.search(inp)
    assert a0.ac.valid
    assert a0.ac.shortname == "b744"

@pytest.mark.parametrize("inp", [
    'b7440',
    'shortname:b7440'
    'name:B747-4000'
])
def test_aircraft_fail_and_suggest(inp):
    a0 = Aircraft.search(inp)
    assert not a0.ac.valid
    suggs = Aircraft.suggest(a0.parse_result)
    assert suggs[0].ac.shortname == "b744"

## airport tests
@pytest.mark.parametrize("inp", [
    'id:3500',
    'iata:Hkg',
    'icao:vhhh',
    'name:hong kong',
    'hong kong'
])
def test_airport_search(inp):
    a0 = Airport.search(inp)
    assert a0.ap.valid
    assert a0.ap.iata == "HKG"

@pytest.mark.parametrize("inp", [
    "VHHX  ",
    "iata:hkgA",
    "icao:VHHx",
    "name:hng kong",
])
def test_airport_fail_and_suggest(inp):
    a0 = Airport.search(inp)
    assert not a0.ap.valid
    suggs = Airport.suggest(a0.parse_result)
    assert suggs[0].ap.iata == "HKG"

## route tests
def test_route():
    a0 = Airport.search('VHHH').ap
    a1 = Airport.search('LHR').ap
    r = Route.from_airports(a0, a1)
    assert int(r.direct_distance) == 9630
    assert r.pax_demand.y == 1093

def test_invalid_route_to_self():
    a0 = Airport.search('VHHH').ap

    with pytest.raises(ValueError):
        _r = Route.from_airports(a0, a0)

def test_route_with_aircraft():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744').ac
    r = Route.from_airports_with_aircraft(ap0, ap1, ac)
    assert int(r.direct_distance) == 9630
    assert r.pax_demand.y == 1093
    cfg = r.aircraft.config.pax_config
    assert cfg.y == 0
    assert cfg.j == 16
    assert cfg.f == 128
    assert cfg.algorithm == PaxConfig.Algorithm.FJY

    ap2 = Airport.search('MTR').ap
    r = Route.from_airports_with_aircraft(ap0, ap2, ac)
    assert int(r.direct_distance) == 16394
    assert r.pax_demand.y == 303
    cfg = r.aircraft.config.pax_config
    assert cfg.y == 303
    assert cfg.j == 56
    assert cfg.f == 1
    assert cfg.algorithm == PaxConfig.Algorithm.YJF

def test_cargo_route_with_aircraft():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744f').ac
    r = Route.from_airports_with_aircraft(ap0, ap1, ac)
    assert r.cargo_demand.l == 547000
    assert r.cargo_demand.h == 681000
    cfg = r.aircraft.config.cargo_config
    assert cfg.l == 100
    assert cfg.h == 0
    assert cfg.algorithm == CargoConfig.Algorithm.L

    ap1 = Airport.search('BPC').ap
    r = Route.from_airports_with_aircraft(ap0, ap1, ac)
    assert r.cargo_demand.l == 148000
    assert r.cargo_demand.h == 220000
    cfg = r.aircraft.config.cargo_config
    assert cfg.l == 70
    assert cfg.h == 30
    assert cfg.algorithm == CargoConfig.Algorithm.L