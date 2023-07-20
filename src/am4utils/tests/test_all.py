import pytest

from am4utils.db import init, reset
from am4utils.demand import CargoDemand
from am4utils.aircraft import (
    Aircraft,
    PaxConfig, CargoConfig
)
from am4utils.airport import Airport
from am4utils.route import Route, AircraftRoute, find_routes
from am4utils.game import Campaign, User

init(db_name='main_test')
reset()

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
    assert a1.ac.fuel == pytest.approx(21.21)
    assert a1.ac.co2 == pytest.approx(0.18)
    assert a1sfc.ac.speed / a1.ac.speed == pytest.approx(1.1)
    assert a1sfc.ac.fuel / a1.ac.fuel == pytest.approx(0.9)
    assert a1sfc.ac.co2 / a1.ac.co2 == pytest.approx(0.9)

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
    cfg = r.config
    assert cfg.y == 0
    assert cfg.j == 1
    assert cfg.f == 138
    assert cfg.algorithm == PaxConfig.Algorithm.FJY

    ap2 = Airport.search('MTR').ap
    r = AircraftRoute.create(ap0, ap2, ac)
    assert int(r.route.direct_distance) == 16394
    assert r.route.pax_demand.y == 303
    cfg = r.config
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
    cfg = r.config
    assert cfg.l == 100
    assert cfg.h == 0
    assert cfg.algorithm == CargoConfig.Algorithm.L

    ap1 = Airport.search('BPC').ap
    r = AircraftRoute.create(ap0, ap1, ac)
    cargo_demand = CargoDemand(r.route.pax_demand)
    assert cargo_demand.l == 148000
    assert cargo_demand.h == 220000
    cfg = r.config
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
    assert r.stopover.full_distance - r.route.direct_distance == pytest.approx(0.00465903702)

    r = AircraftRoute.create(ap0, Airport.search('TNR').ap, ac1)
    assert r.needs_stopover is True
    assert r.stopover.exists is True
    assert r.stopover.airport.iata == "GAN"
    assert r.stopover.full_distance - r.route.direct_distance == pytest.approx(7.550770485)

def test_route_above_specified():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744').ac
    options = AircraftRoute.Options(max_distance=1000)
    r = AircraftRoute.create(ap0, ap1, ac, options)
    assert r.valid is False
    assert AircraftRoute.Warning.ERR_DISTANCE_ABOVE_SPECIFIED in r.warnings

def test_route_too_long():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('c172').ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert r.valid is False
    assert AircraftRoute.Warning.ERR_DISTANCE_TOO_LONG in r.warnings

def test_route_too_short():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('VMMC').ap
    ac = Aircraft.search('b744').ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert r.valid is False
    assert AircraftRoute.Warning.ERR_DISTANCE_TOO_SHORT in r.warnings

def test_route_reduced_contribution():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('RCKH').ap
    ac = Aircraft.search('b744').ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert AircraftRoute.Warning.REDUCED_CONTRIBUTION in r.warnings

def test_route_no_stopover():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('FAEL').ap
    ac = Aircraft.search('mc214').ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert AircraftRoute.Warning.ERR_NO_STOPOVER in r.warnings

def test_route_flight_time_above_specified():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744').ac
    options = AircraftRoute.Options(max_flight_time=1)
    r = AircraftRoute.create(ap0, ap1, ac, options)
    assert r.valid is False
    assert AircraftRoute.Warning.ERR_FLIGHT_TIME_ABOVE_SPECIFIED in r.warnings

def test_route_insufficient_demand():
    ap0 = Airport.search('VHHH').ap
    ap1 = Airport.search('LHR').ap
    ac = Aircraft.search('b744').ac
    options = AircraftRoute.Options(trips_per_day=100)
    r = AircraftRoute.create(ap0, ap1, ac, options)
    assert AircraftRoute.Warning.ERR_INSUFFICIENT_DEMAND in r.warnings

def test_find_routes():
    ap0 = Airport.search('VHHH').ap
    ac = Aircraft.search('mc214').ac
    dests = find_routes(ap0, ac)
    assert len(dests) == 2248
    assert dests[0].airport.iata == "ZND"
    assert dests[0].ac_route.route.direct_distance == pytest.approx(10909.51)

def test_load():
    assert AircraftRoute.estimate_load() == pytest.approx(0.7867845)

# game tests
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

def test_default_user():
    u = User.Default()
    ur = User.Default(True)
    assert u.id == "00000000-0000-0000-0000-000000000000"
    assert u.game_mode == User.GameMode.EASY
    assert ur.id == "00000000-0000-0000-0000-000000000001"
    assert ur.game_mode == User.GameMode.REALISM
    assert u.fuel_price == 700
    assert u.co2_price == 120
    assert u.load == 87
    assert u.role == User.Role.USER

def test_create_user():
    u = User.create("cathayexpress", "<TODO:hashed_password>", 54557, "Cathay Express")
    assert u.username == "cathayexpress"
    assert u.game_id == 54557
    assert u.game_name == "Cathay Express"
    assert u.game_mode == User.GameMode.EASY
    assert u.discord_id == 0

    u_duplicate = User.create("cathayexpress", "<TODO:hashed_password13>", 13, "Cathay Express13")
    assert u_duplicate.valid == False

    u0 = User.from_id(u.id)
    assert u0.id == u.id

    u1 = User.from_username("cathayexpress")
    assert u1.id == u.id

    u2 = User.from_game_id(54557)
    assert u2.id == u.id

    u3 = User.from_game_name("Cathay Express")
    assert u3.id == u.id

    u4 = User.from_discord_id(0)
    assert u4.id == u.id

def test_user_settings():
    u = User.from_username("cathayexpress")
    
    success = u.set_username("cathayexpress13")
    assert success and u.username == "cathayexpress13"

    success = u.set_game_id(13)
    assert success and u.game_id == 13

    success = u.set_game_name("Cathay Express 13")
    assert success and u.game_name == "Cathay Express 13"

    success = u.set_game_mode(User.GameMode.REALISM)
    assert success and u.game_mode == User.GameMode.REALISM

    success = u.set_discord_id(13)
    assert success and u.discord_id == 13

    success = u.set_wear_training(1)
    assert success and u.wear_training == 1

    success = u.set_repair_training(1)
    assert success and u.repair_training == 1

    success = u.set_l_training(1)
    assert success and u.l_training == 1

    success = u.set_h_training(1)
    assert success and u.h_training == 1

    success = u.set_fuel_training(1)
    assert success and u.fuel_training == 1

    success = u.set_co2_training(1)
    assert success and u.co2_training == 1

    success = u.set_fuel_price(512)
    assert success and u.fuel_price == 512

    success = u.set_co2_price(128)
    assert success and u.co2_price == 128

    success = u.set_accumulated_count(13)
    assert success and u.accumulated_count == 13

    success = u.set_load(13)
    assert success and u.load == 13

    success = u.set_role(User.Role.TRUSTED_USER)
    assert success and u.role == User.Role.TRUSTED_USER

def test_user_invalid_settings():
    u = User.from_username("cathayexpress13")

    success = u.set_username("cathayexpress13")
    assert not success

    success = u.set_wear_training(6)
    assert not success

    success = u.set_repair_training(6)
    assert not success

    success = u.set_l_training(7)
    assert not success

    success = u.set_h_training(7)
    assert not success

    success = u.set_fuel_training(4)
    assert not success

    success = u.set_co2_training(6)
    assert not success

    success = u.set_fuel_price(3001)
    assert not success

    success = u.set_co2_price(201)
    assert not success

    success = u.set_load(101)
    assert not success

    success = u.set_load(-1)
    assert not success