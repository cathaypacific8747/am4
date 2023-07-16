from __future__ import annotations
import am4utils._core.ticket
import am4utils._core.game
import typing

__all__ = [
    "CargoTicket",
    "PaxTicket",
    "Ticket",
    "VIPTicket"
]


class CargoTicket():
    def __repr__(self) -> str: ...
    @staticmethod
    def from_optimal(distance: float, game_mode: am4utils._core.game.User.GameMode = am4utils._core.game.User.GameMode.EASY) -> PaxTicket: ...
    def to_dict(self) -> dict: ...
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
    def from_optimal(distance: float, game_mode: am4utils._core.game.User.GameMode = am4utils._core.game.User.GameMode.EASY) -> PaxTicket: ...
    def to_dict(self) -> dict: ...
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
    def to_dict(self) -> dict: ...
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
