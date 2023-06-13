"""Aircraft"""
from __future__ import annotations
import am4utils._core.aircraft
import typing

__all__ = [
    "Aircraft",
    "AircraftNotFoundException",
    "CargoConfig",
    "PaxConfig",
    "PurchasedAircraft",
    "PurchasedAircraftConfig"
]


class Aircraft():
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    @staticmethod
    def _from_all(s: str, priority: int = 0) -> Aircraft: ...
    @staticmethod
    def _from_id(id: int, priority: int = 0) -> Aircraft: ...
    @staticmethod
    def _from_name(s: str, priority: int = 0) -> Aircraft: ...
    @staticmethod
    def _from_shortname(s: str, priority: int = 0) -> Aircraft: ...
    @staticmethod
    def from_auto(s: str) -> Aircraft: ...
    @property
    def capacity(self) -> int:
        """
        :type: int
        """
    @property
    def ceil(self) -> int:
        """
        :type: int
        """
    @property
    def check_cost(self) -> int:
        """
        :type: int
        """
    @property
    def co2(self) -> float:
        """
        :type: float
        """
    @property
    def cost(self) -> int:
        """
        :type: int
        """
    @property
    def crew(self) -> int:
        """
        :type: int
        """
    @property
    def eid(self) -> int:
        """
        :type: int
        """
    @property
    def ename(self) -> str:
        """
        :type: str
        """
    @property
    def engineers(self) -> int:
        """
        :type: int
        """
    @property
    def fuel(self) -> float:
        """
        :type: float
        """
    @property
    def id(self) -> int:
        """
        :type: int
        """
    @property
    def img(self) -> str:
        """
        :type: str
        """
    @property
    def length(self) -> int:
        """
        :type: int
        """
    @property
    def maint(self) -> int:
        """
        :type: int
        """
    @property
    def manufacturer(self) -> str:
        """
        :type: str
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def pilots(self) -> int:
        """
        :type: int
        """
    @property
    def priority(self) -> int:
        """
        :type: int
        """
    @property
    def range(self) -> int:
        """
        :type: int
        """
    @property
    def rwy(self) -> int:
        """
        :type: int
        """
    @property
    def shortname(self) -> str:
        """
        :type: str
        """
    @property
    def speed(self) -> float:
        """
        :type: float
        """
    @property
    def technicians(self) -> int:
        """
        :type: int
        """
    @property
    def type(self) -> am4utils._core.AircraftType:
        """
        :type: am4utils._core.AircraftType
        """
    @property
    def valid(self) -> bool:
        """
        :type: bool
        """
    @property
    def wingspan(self) -> int:
        """
        :type: int
        """
    pass
class AircraftNotFoundException(Exception, BaseException):
    pass
class CargoConfig():
    def __init__(self) -> None: ...
    @property
    def h(self) -> int:
        """
        :type: int
        """
    @property
    def l(self) -> int:
        """
        :type: int
        """
    @property
    def valid(self) -> bool:
        """
        :type: bool
        """
    pass
class PaxConfig():
    def __init__(self) -> None: ...
    @property
    def algorithm(self) -> am4utils._core.PaxConfigAlgorithm:
        """
        :type: am4utils._core.PaxConfigAlgorithm
        """
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
    def valid(self) -> bool:
        """
        :type: bool
        """
    @property
    def y(self) -> int:
        """
        :type: int
        """
    pass
class PurchasedAircraft():
    def __init__(self) -> None: ...
    @property
    def aircraft(self) -> Aircraft:
        """
        :type: Aircraft
        """
    @property
    def config(self) -> PurchasedAircraftConfig:
        """
        :type: PurchasedAircraftConfig
        """
    pass
class PurchasedAircraftConfig():
    def __init__(self) -> None: ...
    @property
    def cargo_config(self) -> CargoConfig:
        """
        :type: CargoConfig
        """
    @property
    def pax_config(self) -> PaxConfig:
        """
        :type: PaxConfig
        """
    pass
