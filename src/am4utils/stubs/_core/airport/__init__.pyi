from __future__ import annotations
import am4utils._core.airport
import typing

__all__ = [
    "Airport",
    "AirportNotFoundException"
]


class Airport():
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    @staticmethod
    def _from_all(s: str) -> Airport: ...
    @staticmethod
    def _from_iata(s: str) -> Airport: ...
    @staticmethod
    def _from_icao(s: str) -> Airport: ...
    @staticmethod
    def _from_id(id: int) -> Airport: ...
    @staticmethod
    def _from_name(s: str) -> Airport: ...
    @staticmethod
    def from_auto(s: str) -> Airport: ...
    @property
    def continent(self) -> str:
        """
        :type: str
        """
    @property
    def country(self) -> str:
        """
        :type: str
        """
    @property
    def fullname(self) -> str:
        """
        :type: str
        """
    @property
    def hub_cost(self) -> int:
        """
        :type: int
        """
    @property
    def iata(self) -> str:
        """
        :type: str
        """
    @property
    def icao(self) -> str:
        """
        :type: str
        """
    @property
    def id(self) -> int:
        """
        :type: int
        """
    @property
    def lat(self) -> float:
        """
        :type: float
        """
    @property
    def lng(self) -> float:
        """
        :type: float
        """
    @property
    def market(self) -> int:
        """
        :type: int
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def rwy(self) -> int:
        """
        :type: int
        """
    @property
    def rwy_codes(self) -> str:
        """
        :type: str
        """
    @property
    def valid(self) -> bool:
        """
        :type: bool
        """
    pass
class AirportNotFoundException(Exception, BaseException):
    pass
