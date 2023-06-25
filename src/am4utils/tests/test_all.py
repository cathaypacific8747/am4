import pytest

import am4utils
from am4utils.db import init
from am4utils.demand import CargoDemand
from am4utils.aircraft import (
    Aircraft,
    PaxConfig, CargoConfig
)
from am4utils.airport import Airport
from am4utils.route import Route
from am4utils.game import Campaign, User

init()

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
    r = Route.create(a0, a1)
    assert int(r.direct_distance) == 9630
    assert r.pax_demand.y == 1093

def test_invalid_route_to_self():
    a0 = Airport.search('VHHH').ap

    with pytest.raises(ValueError):
        _r = Route.create(a0, a0)

def test_route_with_aircraft():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744').ac
    r = Route.create(ap0, ap1).assign(ac)
    assert int(r.route.direct_distance) == 9630
    assert r.route.pax_demand.y == 1093
    cfg = r.aircraft.config.pax_config
    assert cfg.y == 0
    assert cfg.j == 16
    assert cfg.f == 128
    assert cfg.algorithm == PaxConfig.Algorithm.FJY

    ap2 = Airport.search('MTR').ap
    r = Route.create(ap0, ap2).assign(ac)
    assert int(r.route.direct_distance) == 16394
    assert r.route.pax_demand.y == 303
    cfg = r.aircraft.config.pax_config
    assert cfg.y == 303
    assert cfg.j == 56
    assert cfg.f == 1
    assert cfg.algorithm == PaxConfig.Algorithm.YJF

def test_cargo_route_with_aircraft():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744f').ac
    r = Route.create(ap0, ap1).assign(ac)
    cargo_demand = CargoDemand(r.route.pax_demand)
    assert cargo_demand.l == 547000
    assert cargo_demand.h == 681000
    cfg = r.aircraft.config.cargo_config
    assert cfg.l == 100
    assert cfg.h == 0
    assert cfg.algorithm == CargoConfig.Algorithm.L

    ap1 = Airport.search('BPC').ap
    r = Route.create(ap0, ap1).assign(ac)
    cargo_demand = CargoDemand(r.route.pax_demand)
    assert cargo_demand.l == 148000
    assert cargo_demand.h == 220000
    cfg = r.aircraft.config.cargo_config
    assert cfg.l == 70
    assert cfg.h == 30
    assert cfg.algorithm == CargoConfig.Algorithm.L

def test_route_stopover():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    r = Route.create(ap0, ap1).assign(Aircraft.search('b744').ac)
    assert r.needs_stopover is False
    assert r.stopover.exists is False

    ac1 = Aircraft.search('mc214').ac
    r = Route.create(ap0, ap1).assign(ac1)
    assert r.needs_stopover is True
    assert r.stopover.exists is True
    assert r.stopover.airport.iata == "PLX"
    assert 0.00455 < r.stopover.full_distance - r.route.direct_distance < 0.00475

    r = Route.create(ap0, Airport.search('TNR').ap).assign(ac1)
    assert r.needs_stopover is True
    assert r.stopover.exists is True
    assert r.stopover.airport.iata == "GAN"
    assert 7.5 < r.stopover.full_distance - r.route.direct_distance < 7.6

# game tests
def test_default_user():
    c = User()
    assert c.game_mode == User.GameMode.EASY
    assert c.fuel_price == 700
    assert c.co2_price == 120
    assert c.override_load is False
    assert c.load == 85

def test_campaign():
    c = Campaign.parse("c1, e")
    assert c.pax_activated == Campaign.Airline.C1_24HR
    assert c.cargo_activated == Campaign.Airline.C1_24HR
    assert c.eco_activated == Campaign.Eco.C_24HR

    c = Campaign.parse("e")
    assert c.pax_activated == Campaign.Airline.NONE
    assert c.cargo_activated == Campaign.Airline.NONE
    assert c.eco_activated == Campaign.Eco.C_24HR

    c = Campaign.Default()
    assert c.pax_activated == Campaign.Airline.C4_24HR
    assert c.cargo_activated == Campaign.Airline.C4_24HR
    assert c.eco_activated == Campaign.Eco.C_24HR

def test_campaign_reputation():
    c = Campaign.parse("c1, e")
    rep = c.estimate_pax_reputation()
    assert rep == 45 + 7.5 + 10

    c = Campaign.parse("c4, e")
    rep = c.estimate_pax_reputation()
    assert rep == 45 + 30 + 10

    c = Campaign.parse("e")
    rep = c.estimate_pax_reputation()
    assert rep == 45 + 10