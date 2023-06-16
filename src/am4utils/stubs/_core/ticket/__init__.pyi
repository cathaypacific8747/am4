from __future__ import annotations
import am4utils._core.ticket
import typing

__all__ = [
    "CargoTicket",
    "PaxTicket",
    "Ticket",
    "VIPTicket"
]


class CargoTicket():
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
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
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
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
    def __init__(self) -> None: ...
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
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
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
