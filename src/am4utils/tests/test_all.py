import pytest

import am4utils

am4utils.db.init(am4utils.__path__[0])

## airport tests
def test_airport():
    a0 = am4utils.airport._from_id(3500)
    iata = a0.iata
    assert iata == "HKG"

def test_airport_auto_id():
    a0 = am4utils.airport.from_auto('id:3500')
    iata = a0.iata
    assert iata == "HKG"

def test_airport_auto_iata():
    a0 = am4utils.airport.from_auto('iata:Hkg')
    iata = a0.iata
    assert iata == "HKG"

def test_airport_auto_icao():
    a0 = am4utils.airport.from_auto('icao:vhhh')
    iata = a0.iata
    assert iata == "HKG"

def test_airport_auto_name():
    a0 = am4utils.airport.from_auto('name:hong kong')
    iata = a0.iata
    assert iata == "HKG"

def test_airport_auto():
    a0 = am4utils.airport.from_auto('hong kong')
    iata = a0.iata
    assert iata == "HKG"

def test_airport_auto_invalid():
    with pytest.raises(am4utils.AirportNotFoundException):
        _a = am4utils.airport.from_auto('VHHX')

def test_invalid_auto_iata_invalid():
    with pytest.raises(am4utils.AirportNotFoundException):
        _a = am4utils.airport.from_auto('iata:VHHH')


## route tests
def test_route():
    a0 = am4utils.airport.from_auto('VHHH')
    a1 = am4utils.airport.from_auto('LHR')
    r = am4utils.route.from_airports(a0, a1)
    distance = int(r.distance)
    y_demand = r.pax_demand.y
    assert distance == 9630
    assert y_demand == 1093

def test_invalid_route_to_self():
    a0 = am4utils.airport.from_auto('VHHH')

    with pytest.raises(ValueError):
        _r = am4utils.route.from_airports(a0, a0)