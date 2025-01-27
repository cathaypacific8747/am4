import pytest

from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.demand import CargoDemand
from am4.utils.game import User
from am4.utils.route import AircraftRoute, Route, RoutesSearch, SameOdException


def test_route():
    a0 = Airport.search("VHHH").ap
    a1 = Airport.search("LHR").ap
    r = Route.create(a0, a1)
    assert int(r.direct_distance) == 9630
    assert r.pax_demand.y == 1093


def test_invalid_route_to_self():
    a0 = Airport.search("VHHH").ap

    with pytest.raises(SameOdException):
        _r = Route.create(a0, a0)


# WARN: Route.create() uses default user with non-100% load!
def test_route_with_aircraft():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    ac = Aircraft.search("b744").ac
    options = AircraftRoute.Options(tpd_mode=AircraftRoute.Options.TPDMode.STRICT, trips_per_day_per_ac=1)
    r0 = AircraftRoute.create(ap0, ap1, ac, options)
    assert r0.ticket.y == 4422
    assert r0.ticket.j == 8923
    assert r0.ticket.f == 13520
    assert r0.flight_time == pytest.approx(6.53623)
    assert r0.contribution == pytest.approx(30.818565)

    user = User.Default(realism=True)
    r1 = AircraftRoute.create(ap0, ap1, ac, options, user=user)
    assert r1.ticket.y == 3341
    assert r1.ticket.j == 6778
    assert r1.ticket.f == 10245
    assert int(r0.route.direct_distance) == int(r1.route.direct_distance) == 9630
    assert r0.route.pax_demand.y == r1.route.pax_demand.y == 1093
    assert r0.config.y == r1.config.y == 1
    assert r0.config.j == r1.config.j == 14
    assert r0.config.f == r1.config.f == 129
    assert r0.config.algorithm == r1.config.algorithm == Aircraft.PaxConfig.Algorithm.FJY
    assert r1.flight_time / r0.flight_time == pytest.approx(1.5)
    assert r1.contribution / r0.contribution == pytest.approx(1.5)
    assert r0.ci == r1.ci == 200

    ap2 = Airport.search("MTR").ap
    r2 = AircraftRoute.create(ap0, ap2, ac, options)
    assert int(r2.route.direct_distance) == 16394
    assert r2.route.pax_demand.y == 303
    assert r2.config.y == 306
    assert r2.config.j == 55
    assert r2.config.f == 0
    assert r2.config.algorithm == Aircraft.PaxConfig.Algorithm.YJF


def test_route_with_vip_aircraft():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    ac = Aircraft.search("a32vip").ac

    options = AircraftRoute.Options(tpd_mode=AircraftRoute.Options.TPDMode.STRICT, trips_per_day_per_ac=1)
    r = AircraftRoute.create(ap0, ap1, ac, options)
    assert r.ticket.y == 8580
    assert r.ticket.j == 17342
    assert r.ticket.f == 26101


def test_route_with_cargo_aircraft():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    ac = Aircraft.search("b744f").ac

    options = AircraftRoute.Options(tpd_mode=AircraftRoute.Options.TPDMode.STRICT, trips_per_day_per_ac=1)
    r0 = AircraftRoute.create(ap0, ap1, ac, options)
    assert r0.ticket.l == pytest.approx(10.98)
    assert r0.ticket.h == pytest.approx(7.47)

    user = User.Default(realism=True)
    r1 = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r1.ticket.l == pytest.approx(9.15)
    assert r1.ticket.h == pytest.approx(5.65)
    assert r0.config.l == r1.config.l == 100
    assert r0.config.h == r1.config.h == 0


def test_route_with_aircraft_auto():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("TPE").ap
    ac = Aircraft.search("mc214").ac
    options = AircraftRoute.Options(tpd_mode=AircraftRoute.Options.TPDMode.AUTO)
    user = User.Default()

    r = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r.config.y == 69
    assert r.config.j == 37
    assert r.config.f == 29
    assert r.trips_per_day_per_ac == 13


def test_route_with_aircraft_strict_allow_multiple_ac():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("TPE").ap
    ac = Aircraft.search("mc214").ac
    options = AircraftRoute.Options(
        tpd_mode=AircraftRoute.Options.TPDMode.STRICT_ALLOW_MULTIPLE_AC, trips_per_day_per_ac=2
    )
    user = User.Default()

    user.income_loss_tol = 0
    r = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r.config.y == 0
    assert r.config.j == 1
    assert r.config.f == 76
    assert r.trips_per_day_per_ac == 2
    assert r.num_ac == 2

    user.income_loss_tol = 1
    r = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r.config.y == 54
    assert r.config.j == 40
    assert r.config.f == 32
    assert r.trips_per_day_per_ac == 2
    assert r.num_ac == 6

    options.trips_per_day_per_ac = 3
    user.income_loss_tol = 0
    r = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r.config.y == 0
    assert r.config.j == 1
    assert r.config.f == 76
    assert r.trips_per_day_per_ac == 3
    assert r.num_ac == 1

    user.income_loss_tol = 1
    r = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r.config.y == 54
    assert r.config.j == 40
    assert r.config.f == 32
    assert r.trips_per_day_per_ac == 3
    assert r.num_ac == 4


def test_cargo_route_with_aircraft():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    ac = Aircraft.search("b744f").ac
    options = AircraftRoute.Options(tpd_mode=AircraftRoute.Options.TPDMode.STRICT, trips_per_day_per_ac=1)

    r = AircraftRoute.create(ap0, ap1, ac, options)
    cargo_demand = CargoDemand(r.route.pax_demand)
    assert cargo_demand.l == 547000
    assert cargo_demand.h == 681000
    assert r.config.l == 100
    assert r.config.h == 0
    assert r.config.algorithm == Aircraft.CargoConfig.Algorithm.L

    ap1 = Airport.search("BPC").ap
    r = AircraftRoute.create(ap0, ap1, ac, options)
    cargo_demand = CargoDemand(r.route.pax_demand)
    assert cargo_demand.l == 148000
    assert cargo_demand.h == 220000
    assert r.config.l == 71
    assert r.config.h == 29
    assert r.config.algorithm == Aircraft.CargoConfig.Algorithm.L


def test_cargo_route_with_aircraft_auto():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("TPE").ap
    ac = Aircraft.search("b722f").ac
    options = AircraftRoute.Options(tpd_mode=AircraftRoute.Options.TPDMode.AUTO)
    user = User.Default()

    user.income_loss_tol = 1  # allow 100% income loss
    r = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r.config.l == 62
    assert r.config.h == 38
    assert r.trips_per_day_per_ac == 32


def test_cargo_route_with_aircraft_strict_allow_multiple_ac():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("TPE").ap
    ac = Aircraft.search("b722f").ac
    options = AircraftRoute.Options(
        tpd_mode=AircraftRoute.Options.TPDMode.STRICT_ALLOW_MULTIPLE_AC, trips_per_day_per_ac=5
    )
    user = User.Default()

    r = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r.config.l == 100
    assert r.config.h == 0
    assert r.trips_per_day_per_ac == 5
    assert r.num_ac == 4

    user.income_loss_tol = 1
    r = AircraftRoute.create(ap0, ap1, ac, options, user)
    assert r.config.l == 66
    assert r.config.h == 34
    assert r.trips_per_day_per_ac == 5
    assert r.num_ac == 6


def test_route_stopover():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    r = AircraftRoute.create(ap0, ap1, Aircraft.search("b744").ac)
    assert r.needs_stopover is False
    assert r.stopover.exists is False

    ac1 = Aircraft.search("mc214").ac
    r = AircraftRoute.create(ap0, ap1, ac1)
    assert r.needs_stopover is True
    assert r.stopover.exists is True
    assert r.stopover.airport.iata == "PLX"
    assert r.stopover.full_distance - r.route.direct_distance == pytest.approx(0.00465903702)

    r = AircraftRoute.create(ap0, Airport.search("TNR").ap, ac1)
    assert r.needs_stopover is True
    assert r.stopover.exists is True
    assert r.stopover.airport.iata == "GAN"
    assert r.stopover.full_distance - r.route.direct_distance == pytest.approx(7.550770485)


def test_route_realism_rwy_too_short():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("RCLY").ap
    ac = Aircraft.search("b744").ac
    user = User.Default(realism=True)

    r = AircraftRoute.create(ap0, ap1, ac, user=user)
    assert r.valid is False


def test_route_above_specified():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    ac = Aircraft.search("b744").ac
    options = AircraftRoute.Options(max_distance=1000)
    r = AircraftRoute.create(ap0, ap1, ac, options)
    assert r.valid is False
    assert AircraftRoute.Warning.ERR_DISTANCE_ABOVE_SPECIFIED in r.warnings


def test_route_too_long():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    ac = Aircraft.search("c172").ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert r.valid is False
    assert AircraftRoute.Warning.ERR_DISTANCE_TOO_LONG in r.warnings


def test_route_too_short():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("VMMC").ap
    ac = Aircraft.search("b744").ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert r.valid is False
    assert AircraftRoute.Warning.ERR_DISTANCE_TOO_SHORT in r.warnings


def test_route_reduced_contribution():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("RCKH").ap
    ac = Aircraft.search("b744").ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert AircraftRoute.Warning.REDUCED_CONTRIBUTION in r.warnings


def test_route_no_stopover():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("FAEL").ap
    ac = Aircraft.search("mc214").ac
    r = AircraftRoute.create(ap0, ap1, ac)
    assert AircraftRoute.Warning.ERR_NO_STOPOVER in r.warnings


def test_route_flight_time_above_specified():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    ac = Aircraft.search("b744").ac
    options = AircraftRoute.Options(max_flight_time=1)
    r = AircraftRoute.create(ap0, ap1, ac, options)
    assert r.valid is False
    assert AircraftRoute.Warning.ERR_FLIGHT_TIME_ABOVE_SPECIFIED in r.warnings


def test_route_trips_per_day_too_high():
    ap0 = Airport.search("VHHH").ap
    ap1 = Airport.search("LHR").ap
    ac = Aircraft.search("b744").ac
    options = AircraftRoute.Options(tpd_mode=AircraftRoute.Options.TPDMode.STRICT, trips_per_day_per_ac=100)
    r = AircraftRoute.create(ap0, ap1, ac, options)
    assert AircraftRoute.Warning.ERR_TRIPS_PER_DAY_TOO_HIGH in r.warnings


def test_find_routes():
    ap0 = Airport.search("VHHH").ap
    ac = Aircraft.search("mc214").ac
    dests = RoutesSearch([ap0], ac).get()
    assert len(dests) == 2248
    assert dests[0].airport.iata == "TMX"
    assert dests[0].ac_route.route.direct_distance == pytest.approx(10891.46)


def test_export_routes_vip():
    ap0 = Airport.search("CAN").ap
    ac = Aircraft.search("a32vip[sfc]").ac
    options = AircraftRoute.Options(
        tpd_mode=AircraftRoute.Options.TPDMode.STRICT_ALLOW_MULTIPLE_AC, trips_per_day_per_ac=2
    )
    rs = RoutesSearch([ap0], ac, options)
    dests = rs.get()
    assert len(dests) > 10
    cols = rs._get_columns(dests)
    assert len(list(cols.values())[0]) == len(dests)
    assert len(cols) == 34


def test_load():
    assert AircraftRoute.estimate_load() == pytest.approx(0.7867845)
