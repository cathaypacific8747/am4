from __future__ import annotations
import am4utils._core.ticket
import typing
import am4utils._core.user

__all__ = [
    "CargoTicket",
    "PaxTicket",
    "Ticket",
    "VIPTicket"
]


class CargoTicket():
    def __repr__(self) -> str: ...
    @staticmethod
    def from_optimal(distance: float, game_mode: am4utils._core.user.GameMode = am4utils._core.user.GameMode.EASY) -> CargoTicket: ...
    @property
    def h(self) -> float:
        """
        :type: float
        """
    @property
    def l(self) -> float:
        """
        :type: float
        """
    pass
class PaxTicket():
    def __repr__(self) -> str: ...
    @staticmethod
    def from_optimal(distance: float, game_mode: am4utils._core.user.GameMode = am4utils._core.user.GameMode.EASY) -> PaxTicket: ...
    @property
    def f(self) -> int:
        """
        :type: int
        """
    @property
    def j(self) -> int:
        """
        :type: int
        """
    @property
    def y(self) -> int:
        """
        :type: int
        """
    pass
class Ticket():
    @property
    def cargo_ticket(self) -> CargoTicket:
        """
        :type: CargoTicket
        """
    @property
    def pax_ticket(self) -> PaxTicket:
        """
        :type: PaxTicket
        """
    @property
    def vip_ticket(self) -> VIPTicket:
        """
        :type: VIPTicket
        """
    pass
class VIPTicket():
    def __repr__(self) -> str: ...
    @staticmethod
    def from_optimal(distance: float) -> VIPTicket: ...
    @property
    def f(self) -> int:
        """
        :type: int
        """
    @property
    def j(self) -> int:
        """
        :type: int
        """
    @property
    def y(self) -> int:
        """
        :type: int
        """
    pass
