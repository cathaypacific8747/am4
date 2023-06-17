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
    "Route"
]


class AircraftRoute():
    def __repr__(self) -> str: ...
    @staticmethod
    def create(route: Route, ac: am4utils._core.aircraft.Aircraft, trips_per_day: int = 1, user: am4utils._core.game.User = am4utils._core.game.User()) -> AircraftRoute: ...
    @property
    def aircraft(self) -> am4utils._core.aircraft.PurchasedAircraft:
        """
        :type: am4utils._core.aircraft.PurchasedAircraft
        """
    @property
    def income(self) -> float:
        """
        :type: float
        """
    @property
    def route(self) -> Route:
        """
        :type: Route
        """
    @property
    def ticket(self) -> am4utils._core.ticket.Ticket:
        """
        :type: am4utils._core.ticket.Ticket
        """
    pass
class Route():
    def __repr__(self) -> str: ...
    def assign(self, ac: am4utils._core.aircraft.Aircraft, trips_per_day: int = 1, user: am4utils._core.game.User = am4utils._core.game.User()) -> AircraftRoute: ...
    @staticmethod
    def create(ap1: am4utils._core.airport.Airport, ap2: am4utils._core.airport.Airport) -> Route: ...
    @property
    def destination(self) -> am4utils._core.airport.Airport:
        """
        :type: am4utils._core.airport.Airport
        """
    @property
    def direct_distance(self) -> float:
        """
        :type: float
        """
    @property
    def origin(self) -> am4utils._core.airport.Airport:
        """
        :type: am4utils._core.airport.Airport
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
