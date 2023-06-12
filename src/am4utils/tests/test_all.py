import pytest

import am4utils

am4utils.db.init(am4utils.__path__[0])

## airport tests
def test_airport():
    a0 = am4utils.airport._from_id(3500)
    assert a0.iata == "HKG"

def test_airport_auto_id():
    a0 = am4utils.airport.from_auto('id:3500')
    assert a0.iata == "HKG"

def test_airport_auto_iata():
    a0 = am4utils.airport.from_auto('iata:Hkg')
    assert a0.iata == "HKG"

def test_airport_auto_icao():
    a0 = am4utils.airport.from_auto('icao:vhhh')
    assert a0.iata == "HKG"

def test_airport_auto_name():
    a0 = am4utils.airport.from_auto('name:hong kong')
    assert a0.iata == "HKG"

def test_airport_auto():
    a0 = am4utils.airport.from_auto('hong kong')
    assert a0.iata == "HKG"

def test_airport_auto_invalid():
    with pytest.raises(am4utils.airport.AirportNotFoundException):
        _a = am4utils.airport.from_auto('VHHX')

def test_invalid_auto_iata_invalid():
    with pytest.raises(am4utils.airport.AirportNotFoundException):
        _a = am4utils.airport.from_auto('iata:VHHH')


## aircraft tests
def test_aircraft():
    a0 = am4utils.aircraft._from_id(1)
    assert a0.shortname == "b744"

def test_aircraft_auto_id():
    a0 = am4utils.aircraft.from_auto('id:1')
    assert a0.shortname == "b744"

def test_aircraft_auto_shortname():
    a0 = am4utils.aircraft.from_auto('shortname:b744')
    assert a0.shortname == "b744"

def test_aircraft_auto_name():
    a0 = am4utils.aircraft.from_auto('name:B747-400')
    assert a0.shortname == "b744"

def test_aircraft_auto_fail():
    with pytest.raises(am4utils.aircraft.AircraftNotFoundException):
        _a = am4utils.aircraft.from_auto('b745')

def test_aircraft_auto_shortname_fail():
    with pytest.raises(am4utils.aircraft.AircraftNotFoundException):
        _a = am4utils.aircraft.from_auto('shortname:b745')

## route tests
def test_route():
    a0 = am4utils.airport.from_auto('VHHH')
    a1 = am4utils.airport.from_auto('LHR')
    r = am4utils.route.from_airports(a0, a1)
    assert int(r.distance) == 9630
    assert r.pax_demand.y == 1093

def test_invalid_route_to_self():
    a0 = am4utils.airport.from_auto('VHHH')

    with pytest.raises(ValueError):
        _r = am4utils.route.from_airports(a0, a0)

def test_route_with_aircraft():
    a0 = am4utils.airport.from_auto('VHHH')
    a1 = am4utils.airport.from_auto('LHR')
    ac = am4utils.aircraft.from_auto('b744')
    r = am4utils.route.from_airports_with_aircraft(a0, a1, ac)
    assert int(r.distance) == 9630
    assert r.pax_demand.y == 1093