from __future__ import annotations
import am4utils._core.route
import typing
import am4utils._core.aircraft
import am4utils._core.airport
import am4utils._core.user

__all__ = [
    "Route"
]


class Route():
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    @staticmethod
    def create_optimal_cargo_ticket(distance: float, game_mode: am4utils._core.user.GameMode) -> CargoTicket: ...
    @staticmethod
    def create_optimal_pax_ticket(distance: float, game_mode: am4utils._core.user.GameMode) -> PaxTicket: ...
    @staticmethod
    def from_airports(ap1: am4utils._core.airport.Airport, ap2: am4utils._core.airport.Airport) -> Route: ...
    @staticmethod
    def from_airports_with_aircraft(ap1: am4utils._core.airport.Airport, ap2: am4utils._core.airport.Airport, ac: am4utils._core.aircraft.Aircraft, trips_per_day: int = 1, game_mode: am4utils._core.user.GameMode = GameMode.EASY) -> Route: ...
    @property
    def aircraft(self) -> am4utils._core.aircraft.PurchasedAircraft:
        """
        :type: am4utils._core.aircraft.PurchasedAircraft
        """
    @property
    def cargo_demand(self) -> CargoDemand:
        """
        :type: CargoDemand
        """
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
    def income(self) -> int:
        """
        :type: int
        """
    @property
    def origin(self) -> am4utils._core.airport.Airport:
        """
        :type: am4utils._core.airport.Airport
        """
    @property
    def pax_demand(self) -> PaxDemand:
        """
        :type: PaxDemand
        """
    @property
    def ticket(self) -> Ticket:
        """
        :type: Ticket
        """
    @property
    def valid(self) -> bool:
        """
        :type: bool
        """
    pass
