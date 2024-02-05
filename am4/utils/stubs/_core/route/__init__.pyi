from __future__ import annotations
import am4utils._core.route
import typing
import am4utils._core.aircraft
import am4utils._core.airport
import am4utils._core.game
import am4utils._core.ticket
import am4utils._core.demand

__all__ = [
    "AircraftRoute",
    "Destination",
    "Route",
    "find_routes"
]


class AircraftRoute():
    class Options():
        class TPDMode():
            """
            Members:

              AUTO

              AUTO_MULTIPLE_OF

              STRICT
            """
            def __eq__(self, other: object) -> bool: ...
            def __getstate__(self) -> int: ...
            def __hash__(self) -> int: ...
            def __index__(self) -> int: ...
            def __init__(self, value: int) -> None: ...
            def __int__(self) -> int: ...
            def __ne__(self, other: object) -> bool: ...
            def __repr__(self) -> str: ...
            def __setstate__(self, state: int) -> None: ...
            @property
            def name(self) -> str:
                """
                :type: str
                """
            @property
            def value(self) -> int:
                """
                :type: int
                """
            AUTO: am4utils._core.route.AircraftRoute.Options.TPDMode # value = <TPDMode.AUTO: 0>
            AUTO_MULTIPLE_OF: am4utils._core.route.AircraftRoute.Options.TPDMode # value = <TPDMode.AUTO_MULTIPLE_OF: 1>
            STRICT: am4utils._core.route.AircraftRoute.Options.TPDMode # value = <TPDMode.STRICT: 2>
            __members__: dict # value = {'AUTO': <TPDMode.AUTO: 0>, 'AUTO_MULTIPLE_OF': <TPDMode.AUTO_MULTIPLE_OF: 1>, 'STRICT': <TPDMode.STRICT: 2>}
            pass
        def __init__(self, tpd_mode: AircraftRoute.Options.TPDMode = TPDMode.AUTO, trips_per_day: int = 1, max_distance: float = 20015.086796020572, max_flight_time: float = 24.0, config_algorithm: typing.Union[None, am4utils._core.aircraft.Aircraft.PaxConfig.Algorithm, am4utils._core.aircraft.Aircraft.CargoConfig.Algorithm] = None) -> None: ...
        @property
        def config_algorithm(self) -> typing.Union[None, am4utils._core.aircraft.Aircraft.PaxConfig.Algorithm, am4utils._core.aircraft.Aircraft.CargoConfig.Algorithm]:
            """
            :type: typing.Union[None, am4utils._core.aircraft.Aircraft.PaxConfig.Algorithm, am4utils._core.aircraft.Aircraft.CargoConfig.Algorithm]
            """
        @config_algorithm.setter
        def config_algorithm(self, arg0: typing.Union[None, am4utils._core.aircraft.Aircraft.PaxConfig.Algorithm, am4utils._core.aircraft.Aircraft.CargoConfig.Algorithm]) -> None:
            pass
        @property
        def max_distance(self) -> float:
            """
            :type: float
            """
        @max_distance.setter
        def max_distance(self, arg0: float) -> None:
            pass
        @property
        def max_flight_time(self) -> float:
            """
            :type: float
            """
        @max_flight_time.setter
        def max_flight_time(self, arg0: float) -> None:
            pass
        @property
        def tpd_mode(self) -> AircraftRoute.Options.TPDMode:
            """
            :type: AircraftRoute.Options.TPDMode
            """
        @tpd_mode.setter
        def tpd_mode(self, arg0: AircraftRoute.Options.TPDMode) -> None:
            pass
        @property
        def trips_per_day(self) -> int:
            """
            :type: int
            """
        @trips_per_day.setter
        def trips_per_day(self, arg0: int) -> None:
            pass
        pass
    class Stopover():
        def __repr__(self) -> str: ...
        @staticmethod
        def find_by_efficiency(origin: am4utils._core.airport.Airport, destination: am4utils._core.airport.Airport, aircraft: am4utils._core.aircraft.Aircraft, game_mode: am4utils._core.game.User.GameMode) -> AircraftRoute.Stopover: ...
        def to_dict(self) -> dict: ...
        @property
        def airport(self) -> am4utils._core.airport.Airport:
            """
            :type: am4utils._core.airport.Airport
            """
        @property
        def exists(self) -> bool:
            """
            :type: bool
            """
        @property
        def full_distance(self) -> float:
            """
            :type: float
            """
        pass
    class Warning():
        """
        Members:

          ERR_RWY_TOO_SHORT

          ERR_DISTANCE_ABOVE_SPECIFIED

          ERR_DISTANCE_TOO_LONG

          ERR_DISTANCE_TOO_SHORT

          REDUCED_CONTRIBUTION

          ERR_NO_STOPOVER

          ERR_FLIGHT_TIME_ABOVE_SPECIFIED

          ERR_INSUFFICIENT_DEMAND
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
        def __init__(self, value: int) -> None: ...
        def __int__(self) -> int: ...
        def __ne__(self, other: object) -> bool: ...
        def __repr__(self) -> str: ...
        def __setstate__(self, state: int) -> None: ...
        @property
        def name(self) -> str:
            """
            :type: str
            """
        @property
        def value(self) -> int:
            """
            :type: int
            """
        ERR_DISTANCE_ABOVE_SPECIFIED: am4utils._core.route.AircraftRoute.Warning # value = <Warning.ERR_DISTANCE_ABOVE_SPECIFIED: 1>
        ERR_DISTANCE_TOO_LONG: am4utils._core.route.AircraftRoute.Warning # value = <Warning.ERR_DISTANCE_TOO_LONG: 2>
        ERR_DISTANCE_TOO_SHORT: am4utils._core.route.AircraftRoute.Warning # value = <Warning.ERR_DISTANCE_TOO_SHORT: 3>
        ERR_FLIGHT_TIME_ABOVE_SPECIFIED: am4utils._core.route.AircraftRoute.Warning # value = <Warning.ERR_FLIGHT_TIME_ABOVE_SPECIFIED: 6>
        ERR_INSUFFICIENT_DEMAND: am4utils._core.route.AircraftRoute.Warning # value = <Warning.ERR_INSUFFICIENT_DEMAND: 7>
        ERR_NO_STOPOVER: am4utils._core.route.AircraftRoute.Warning # value = <Warning.ERR_NO_STOPOVER: 5>
        ERR_RWY_TOO_SHORT: am4utils._core.route.AircraftRoute.Warning # value = <Warning.ERR_RWY_TOO_SHORT: 0>
        REDUCED_CONTRIBUTION: am4utils._core.route.AircraftRoute.Warning # value = <Warning.REDUCED_CONTRIBUTION: 4>
        __members__: dict # value = {'ERR_RWY_TOO_SHORT': <Warning.ERR_RWY_TOO_SHORT: 0>, 'ERR_DISTANCE_ABOVE_SPECIFIED': <Warning.ERR_DISTANCE_ABOVE_SPECIFIED: 1>, 'ERR_DISTANCE_TOO_LONG': <Warning.ERR_DISTANCE_TOO_LONG: 2>, 'ERR_DISTANCE_TOO_SHORT': <Warning.ERR_DISTANCE_TOO_SHORT: 3>, 'REDUCED_CONTRIBUTION': <Warning.REDUCED_CONTRIBUTION: 4>, 'ERR_NO_STOPOVER': <Warning.ERR_NO_STOPOVER: 5>, 'ERR_FLIGHT_TIME_ABOVE_SPECIFIED': <Warning.ERR_FLIGHT_TIME_ABOVE_SPECIFIED: 6>, 'ERR_INSUFFICIENT_DEMAND': <Warning.ERR_INSUFFICIENT_DEMAND: 7>}
        pass
    def __repr__(self) -> str: ...
    @staticmethod
    @typing.overload
    def calc_co2(ac: am4utils._core.aircraft.Aircraft, cfg: am4utils._core.aircraft.Aircraft.PaxConfig, distance: float, user: am4utils._core.game.User = am4utils._core.game.User.Default(), ci: int = 200) -> float: ...
    @staticmethod
    @typing.overload
    def calc_co2(ac: am4utils._core.aircraft.Aircraft, cfg: am4utils._core.aircraft.Aircraft.CargoConfig, distance: float, user: am4utils._core.game.User = am4utils._core.game.User.Default(), ci: int = 200) -> float: ...
    @staticmethod
    def calc_fuel(ac: am4utils._core.aircraft.Aircraft, distance: float, user: am4utils._core.game.User = am4utils._core.game.User.Default(), ci: int = 200) -> float: ...
    @staticmethod
    def create(ap0: am4utils._core.airport.Airport, ap1: am4utils._core.airport.Airport, ac: am4utils._core.aircraft.Aircraft, options: AircraftRoute.Options = AircraftRoute.Options(), user: am4utils._core.game.User = am4utils._core.game.User.Default()) -> AircraftRoute: ...
    @staticmethod
    def estimate_load(reputation: float = 87, autoprice_ratio: float = 1.06, has_stopover: bool = False) -> float: ...
    def to_dict(self) -> dict: ...
    @property
    def acheck_cost(self) -> float:
        """
        :type: float
        """
    @property
    def ci(self) -> int:
        """
        :type: int
        """
    @property
    def co2(self) -> float:
        """
        :type: float
        """
    @property
    def config(self) -> typing.Union[am4utils._core.aircraft.Aircraft.PaxConfig, am4utils._core.aircraft.Aircraft.CargoConfig]:
        """
        :type: typing.Union[am4utils._core.aircraft.Aircraft.PaxConfig, am4utils._core.aircraft.Aircraft.CargoConfig]
        """
    @property
    def contribution(self) -> float:
        """
        :type: float
        """
    @property
    def flight_time(self) -> float:
        """
        :type: float
        """
    @property
    def fuel(self) -> float:
        """
        :type: float
        """
    @property
    def income(self) -> float:
        """
        :type: float
        """
    @property
    def max_income(self) -> float:
        """
        :type: float
        """
    @property
    def needs_stopover(self) -> bool:
        """
        :type: bool
        """
    @property
    def profit(self) -> float:
        """
        :type: float
        """
    @property
    def repair_cost(self) -> float:
        """
        :type: float
        """
    @property
    def route(self) -> Route:
        """
        :type: Route
        """
    @property
    def stopover(self) -> AircraftRoute.Stopover:
        """
        :type: AircraftRoute.Stopover
        """
    @property
    def ticket(self) -> typing.Union[am4utils._core.ticket.PaxTicket, am4utils._core.ticket.CargoTicket, am4utils._core.ticket.VIPTicket]:
        """
        :type: typing.Union[am4utils._core.ticket.PaxTicket, am4utils._core.ticket.CargoTicket, am4utils._core.ticket.VIPTicket]
        """
    @property
    def trips_per_day(self) -> int:
        """
        :type: int
        """
    @property
    def valid(self) -> bool:
        """
        :type: bool
        """
    @property
    def warnings(self) -> typing.List[AircraftRoute.Warning]:
        """
        :type: typing.List[AircraftRoute.Warning]
        """
    pass
class Destination():
    def to_dict(self) -> dict: ...
    @property
    def ac_route(self) -> AircraftRoute:
        """
        :type: AircraftRoute
        """
    @property
    def airport(self) -> am4utils._core.airport.Airport:
        """
        :type: am4utils._core.airport.Airport
        """
    pass
class Route():
    def __repr__(self) -> str: ...
    @staticmethod
    def create(ap0: am4utils._core.airport.Airport, ap1: am4utils._core.airport.Airport) -> Route: ...
    def to_dict(self) -> dict: ...
    @property
    def direct_distance(self) -> float:
        """
        :type: float
        """
    @property
    def pax_demand(self) -> am4utils._core.demand.PaxDemand:
        """
        :type: am4utils._core.demand.PaxDemand
        """
    @property
    def valid(self) -> bool:
        """
        :type: bool
        """
    pass
def find_routes(ap0: am4utils._core.airport.Airport, ac: am4utils._core.aircraft.Aircraft, options: AircraftRoute.Options = AircraftRoute.Options(), user: am4utils._core.game.User = am4utils._core.game.User.Default()) -> typing.List[Destination]:
    pass
