import pytest

import am4utils
from am4utils._core.aircraft import Aircraft
from am4utils._core.airport import Airport
from am4utils._core.route import Route

am4utils.db.init(am4utils.__path__[0])

## aircraft tests
def test_aircraft():
    a0 = Aircraft._from_id(1)
    assert a0.shortname == "b744"

def test_aircraft_auto_id():
    a0 = Aircraft.from_auto('id:1')
    assert a0.shortname == "b744"

def test_aircraft_auto_shortname():
    a0 = Aircraft.from_auto('shortname:b744')
    assert a0.shortname == "b744"

def test_aircraft_auto_name():
    a0 = Aircraft.from_auto('name:B747-400')
    assert a0.shortname == "b744"

def test_aircraft_auto_fail():
    with pytest.raises(am4utils.aircraft.AircraftNotFoundException):
        _a = Aircraft.from_auto('b745')

def test_aircraft_auto_shortname_fail():
    with pytest.raises(am4utils.aircraft.AircraftNotFoundException):
        _a = Aircraft.from_auto('shortname:b745')

## airport tests
def test_airport():
    a0 = Airport._from_id(3500)
    assert a0.iata == "HKG"

def test_airport_auto_id():
    a0 = Airport.from_auto('id:3500')
    assert a0.iata == "HKG"

def test_airport_auto_iata():
    a0 = Airport.from_auto('iata:Hkg')
    assert a0.iata == "HKG"

def test_airport_auto_icao():
    a0 = Airport.from_auto('icao:vhhh')
    assert a0.iata == "HKG"

def test_airport_auto_name():
    a0 = Airport.from_auto('name:hong kong')
    assert a0.iata == "HKG"

def test_airport_auto():
    a0 = Airport.from_auto('hong kong')
    assert a0.iata == "HKG"

def test_airport_auto_invalid():
    with pytest.raises(am4utils.airport.AirportNotFoundException):
        _a = Airport.from_auto('VHHX')

def test_invalid_auto_iata_invalid():
    with pytest.raises(am4utils.airport.AirportNotFoundException):
        _a = Airport.from_auto('iata:VHHH')


## route tests
def test_route():
    a0 = Airport.from_auto('VHHH')
    a1 = Airport.from_auto('LHR')
    r = Route.from_airports(a0, a1)
    assert int(r.distance) == 9630
    assert r.pax_demand.y == 1093

def test_invalid_route_to_self():
    a0 = Airport.from_auto('VHHH')

    with pytest.raises(ValueError):
        _r = Route.from_airports(a0, a0)

def test_route_with_aircraft():
    a0 = Airport.from_auto('VHHH')
    a1 = Airport.from_auto('LHR')
    ac = Aircraft.from_auto('b744')
    r = Route.from_airports_with_aircraft(a0, a1, ac)
    assert int(r.distance) == 9630
    assert r.pax_demand.y == 1093
    assert r.purchased_aircraft.config.pax_config.y == 0
    assert r.purchased_aircraft.config.pax_config.j == 16
    assert r.purchased_aircraft.config.pax_config.f == 128