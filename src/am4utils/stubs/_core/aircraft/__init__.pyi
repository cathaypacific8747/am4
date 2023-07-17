from __future__ import annotations
import am4utils._core.aircraft
import typing

__all__ = [
    "Aircraft",
    "CargoConfig",
    "PaxConfig"
]


class Aircraft():
    class Config():
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
    class ParseResult():
        @property
        def co2_mod(self) -> bool:
            """
            :type: bool
            """
        @property
        def fuel_mod(self) -> bool:
            """
            :type: bool
            """
        @property
        def priority(self) -> int:
            """
            :type: int
            """
        @property
        def search_str(self) -> str:
            """
            :type: str
            """
        @property
        def search_type(self) -> Aircraft.SearchType:
            """
            :type: Aircraft.SearchType
            """
        @property
        def speed_mod(self) -> bool:
            """
            :type: bool
            """
        pass
    class SearchResult():
        def __init__(self, arg0: Aircraft, arg1: Aircraft.ParseResult) -> None: ...
        @property
        def ac(self) -> Aircraft:
            """
            :type: Aircraft
            """
        @property
        def parse_result(self) -> Aircraft.ParseResult:
            """
            :type: Aircraft.ParseResult
            """
        pass
    class SearchType():
        """
        Members:

          ALL

          ID

          SHORTNAME

          NAME
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
        ALL: am4utils._core.aircraft.Aircraft.SearchType # value = <SearchType.ALL: 0>
        ID: am4utils._core.aircraft.Aircraft.SearchType # value = <SearchType.ID: 1>
        NAME: am4utils._core.aircraft.Aircraft.SearchType # value = <SearchType.NAME: 3>
        SHORTNAME: am4utils._core.aircraft.Aircraft.SearchType # value = <SearchType.SHORTNAME: 2>
        __members__: dict # value = {'ALL': <SearchType.ALL: 0>, 'ID': <SearchType.ID: 1>, 'SHORTNAME': <SearchType.SHORTNAME: 2>, 'NAME': <SearchType.NAME: 3>}
        pass
    class Suggestion():
        def __init__(self, arg0: Aircraft, arg1: float) -> None: ...
        @property
        def ac(self) -> Aircraft:
            """
            :type: Aircraft
            """
        @property
        def score(self) -> float:
            """
            :type: float
            """
        pass
    class Type():
        """
        Members:

          PAX

          CARGO

          VIP
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
        CARGO: am4utils._core.aircraft.Aircraft.Type # value = <Type.CARGO: 1>
        PAX: am4utils._core.aircraft.Aircraft.Type # value = <Type.PAX: 0>
        VIP: am4utils._core.aircraft.Aircraft.Type # value = <Type.VIP: 2>
        __members__: dict # value = {'PAX': <Type.PAX: 0>, 'CARGO': <Type.CARGO: 1>, 'VIP': <Type.VIP: 2>}
        pass
    def __repr__(self) -> str: ...
    @staticmethod
    def search(s: str) -> Aircraft.SearchResult: ...
    @staticmethod
    def suggest(s: Aircraft.ParseResult) -> typing.List[Aircraft.Suggestion]: ...
    def to_dict(self) -> dict: ...
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
    def co2_mod(self) -> bool:
        """
        :type: bool
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
    def fuel_mod(self) -> bool:
        """
        :type: bool
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
    def speed_mod(self) -> bool:
        """
        :type: bool
        """
    @property
    def technicians(self) -> int:
        """
        :type: int
        """
    @property
    def type(self) -> Aircraft.Type:
        """
        :type: Aircraft.Type
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
class CargoConfig():
    class Algorithm():
        """
        Members:

          L

          H

          NONE
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
        H: am4utils._core.aircraft.CargoConfig.Algorithm # value = <Algorithm.H: 1>
        L: am4utils._core.aircraft.CargoConfig.Algorithm # value = <Algorithm.L: 0>
        NONE: am4utils._core.aircraft.CargoConfig.Algorithm # value = <Algorithm.NONE: 2>
        __members__: dict # value = {'L': <Algorithm.L: 0>, 'H': <Algorithm.H: 1>, 'NONE': <Algorithm.NONE: 2>}
        pass
    def __repr__(self) -> str: ...
    def to_dict(self) -> dict: ...
    @property
    def algorithm(self) -> CargoConfig.Algorithm:
        """
        :type: CargoConfig.Algorithm
        """
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
    class Algorithm():
        """
        Members:

          FJY

          FYJ

          JFY

          JYF

          YJF

          YFJ

          NONE
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
        FJY: am4utils._core.aircraft.PaxConfig.Algorithm # value = <Algorithm.FJY: 0>
        FYJ: am4utils._core.aircraft.PaxConfig.Algorithm # value = <Algorithm.FYJ: 1>
        JFY: am4utils._core.aircraft.PaxConfig.Algorithm # value = <Algorithm.JFY: 2>
        JYF: am4utils._core.aircraft.PaxConfig.Algorithm # value = <Algorithm.JYF: 3>
        NONE: am4utils._core.aircraft.PaxConfig.Algorithm # value = <Algorithm.NONE: 6>
        YFJ: am4utils._core.aircraft.PaxConfig.Algorithm # value = <Algorithm.YFJ: 5>
        YJF: am4utils._core.aircraft.PaxConfig.Algorithm # value = <Algorithm.YJF: 4>
        __members__: dict # value = {'FJY': <Algorithm.FJY: 0>, 'FYJ': <Algorithm.FYJ: 1>, 'JFY': <Algorithm.JFY: 2>, 'JYF': <Algorithm.JYF: 3>, 'YJF': <Algorithm.YJF: 4>, 'YFJ': <Algorithm.YFJ: 5>, 'NONE': <Algorithm.NONE: 6>}
        pass
    def __repr__(self) -> str: ...
    def to_dict(self) -> dict: ...
    @property
    def algorithm(self) -> PaxConfig.Algorithm:
        """
        :type: PaxConfig.Algorithm
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
