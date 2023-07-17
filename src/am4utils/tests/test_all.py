import pytest

import am4utils
from am4utils.db import init
from am4utils.demand import CargoDemand
from am4utils.aircraft import (
    Aircraft,
    PaxConfig, CargoConfig
)
from am4utils.airport import Airport
from am4utils.route import Route, AircraftRoute
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

@pytest.mark.parametrize("inp", [
    'b744[sfc]',
    'b744[s,fc]',
    'b744[sf,c]',
    'b744[s,f,c]',
    'b744[s, f, c]',
    'b744[ , s, f,, c,,,  ]',
    'id:1[sfc]',
    'shortname:b744[sfc]',
    'name:B747-400[sfc]',
])
def test_aircraft_modifiers_syntax(inp):
    a0 = Aircraft.search(inp)
    assert a0.ac.shortname == "b744"
    assert a0.parse_result.speed_mod is True
    assert a0.ac.speed_mod is True
    assert a0.parse_result.fuel_mod is True
    assert a0.ac.fuel_mod is True
    assert a0.parse_result.co2_mod is True
    assert a0.ac.co2_mod is True

def test_aircraft_engine_modifier():
    a = Aircraft.search('b744')
    a0 = Aircraft.search('b744[0]')
    a1 = Aircraft.search('b744[1]')
    a1sfc = Aircraft.search('b744[1,sfc]')
    assert a0.ac.id == a1.ac.id == a.ac.id == 1
    assert a0.ac.eid == a.ac.eid == 4
    assert a1.ac.eid == 2
    assert abs(a1.ac.fuel - 21.21) < 0.001
    assert abs(a1.ac.co2 - 0.18) < 0.001
    assert abs(a1sfc.ac.speed / a1.ac.speed - 1.1) < 0.001
    assert abs(a1sfc.ac.fuel / a1.ac.fuel - 0.9) < 0.001
    assert abs(a1sfc.ac.co2 / a1.ac.co2 - 0.9) < 0.001

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

# WARN: Route.create() uses default user with non-100% load!
def test_route_with_aircraft():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744').ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert int(r.route.direct_distance) == 9630
    assert r.route.pax_demand.y == 1093
    cfg = r.config.pax_config
    assert cfg.y == 0
    assert cfg.j == 1
    assert cfg.f == 138
    assert cfg.algorithm == PaxConfig.Algorithm.FJY

    ap2 = Airport.search('MTR').ap
    r = AircraftRoute.create(ap0, ap2, ac)
    assert int(r.route.direct_distance) == 16394
    assert r.route.pax_demand.y == 303
    cfg = r.config.pax_config
    assert cfg.y == 348
    assert cfg.j == 34
    assert cfg.f == 0
    assert cfg.algorithm == PaxConfig.Algorithm.YJF

def test_cargo_route_with_aircraft():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744f').ac
    r = AircraftRoute.create(ap0, ap1, ac)
    cargo_demand = CargoDemand(r.route.pax_demand)
    assert cargo_demand.l == 547000
    assert cargo_demand.h == 681000
    cfg = r.config.cargo_config
    assert cfg.l == 100
    assert cfg.h == 0
    assert cfg.algorithm == CargoConfig.Algorithm.L

    ap1 = Airport.search('BPC').ap
    r = AircraftRoute.create(ap0, ap1, ac)
    cargo_demand = CargoDemand(r.route.pax_demand)
    assert cargo_demand.l == 148000
    assert cargo_demand.h == 220000
    cfg = r.config.cargo_config
    assert cfg.l == 80
    assert cfg.h == 20
    assert cfg.algorithm == CargoConfig.Algorithm.L

def test_route_stopover():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    r = AircraftRoute.create(ap0, ap1, Aircraft.search('b744').ac)
    assert r.needs_stopover is False
    assert r.stopover.exists is False

    ac1 = Aircraft.search('mc214').ac
    r = AircraftRoute.create(ap0, ap1, ac1)
    assert r.needs_stopover is True
    assert r.stopover.exists is True
    assert r.stopover.airport.iata == "PLX"
    assert 0.00455 < r.stopover.full_distance - r.route.direct_distance < 0.00475

    r = AircraftRoute.create(ap0, Airport.search('TNR').ap, ac1)
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
    assert c.load == 87

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

def test_load():
    assert AircraftRoute.estimate_load() == 0.7867845