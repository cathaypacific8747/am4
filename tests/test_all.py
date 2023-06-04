import am4utils
import pytest

am4utils.db.init()

def test_airport():
    a0 = am4utils.airport._from_id(3500)
    iata = a0.iata
    assert iata == "HKG"

def test_invalid_airport():
    with pytest.raises(am4utils.AirportNotFoundException):
        a0 = am4utils.airport.from_auto('VHHX')

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
        r = am4utils.route.from_airports(a0, a0)