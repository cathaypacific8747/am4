import pytest

import am4utils
from am4utils.aircraft import (
    Aircraft, AircraftNotFoundException,
    PaxConfig, CargoConfig
)
from am4utils.airport import Airport, AirportNotFoundException
from am4utils.route import Route

am4utils.db.init(am4utils.__path__[0])

## aircraft tests
@pytest.mark.parametrize("inp", [
    'id:1',
    'shortname:b744',
    'name:B747-400'
])
def test_aircraft_auto(inp):
    a0 = Aircraft.from_auto(inp)
    assert a0.shortname == "b744"

@pytest.mark.parametrize("inp", [
    'b745',
    'shortname:b745'
    'name:B747-500'
])
def test_aircraft_fail(inp):
    with pytest.raises(AircraftNotFoundException):
        _a = Aircraft.from_auto(inp)


## airport tests
@pytest.mark.parametrize("inp", [
    'id:3500',
    'iata:Hkg',
    'icao:vhhh',
    'name:hong kong',
    'hong kong'
])
def test_airport_auto(inp):
    a0 = Airport.from_auto(inp)
    assert a0.iata == "HKG"

@pytest.mark.parametrize("inp", [
    "VHHX",
    "iata:VHHX",
    "icao:VHHX",
])
def test_airport_fail(inp):
    with pytest.raises(AirportNotFoundException):
        _a = Airport.from_auto(inp)

## route tests
def test_route():
    a0 = Airport.from_auto('VHHH')
    a1 = Airport.from_auto('LHR')
    r = Route.from_airports(a0, a1)
    assert int(r.direct_distance) == 9630
    assert r.pax_demand.y == 1093

def test_invalid_route_to_self():
    a0 = Airport.from_auto('VHHH')

    with pytest.raises(ValueError):
        _r = Route.from_airports(a0, a0)

def test_route_with_aircraft():
    ap0 = Airport.from_auto('VHHH')
    ap1 = Airport.from_auto('LHR')
    ac = Aircraft.from_auto('b744')
    r = Route.from_airports_with_aircraft(ap0, ap1, ac)
    assert int(r.direct_distance) == 9630
    assert r.pax_demand.y == 1093
    cfg = r.aircraft.config.pax_config
    assert cfg.y == 0
    assert cfg.j == 16
    assert cfg.f == 128
    assert cfg.algorithm == PaxConfig.Algorithm.FJY

    ap2 = Airport.from_auto('MTR')
    r = Route.from_airports_with_aircraft(ap0, ap2, ac)
    assert int(r.direct_distance) == 16394
    assert r.pax_demand.y == 303
    cfg = r.aircraft.config.pax_config
    assert cfg.y == 303
    assert cfg.j == 56
    assert cfg.f == 1
    assert cfg.algorithm == PaxConfig.Algorithm.YJF