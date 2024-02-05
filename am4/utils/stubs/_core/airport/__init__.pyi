from __future__ import annotations
import am4utils._core.airport
import typing

__all__ = [
    "Airport"
]


class Airport():
    class ParseResult():
        def __init__(self, arg0: Airport.SearchType, arg1: str) -> None: ...
        @property
        def search_str(self) -> str:
            """
            :type: str
            """
        @property
        def search_type(self) -> Airport.SearchType:
            """
            :type: Airport.SearchType
            """
        pass
    class SearchResult():
        def __init__(self, arg0: Airport, arg1: Airport.ParseResult) -> None: ...
        @property
        def ap(self) -> Airport:
            """
            :type: Airport
            """
        @property
        def parse_result(self) -> Airport.ParseResult:
            """
            :type: Airport.ParseResult
            """
        pass
    class SearchType():
        """
        Members:

          ALL

          IATA

          ICAO

          NAME

          FULLNAME

          ID
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
        ALL: am4utils._core.airport.Airport.SearchType # value = <SearchType.ALL: 0>
        FULLNAME: am4utils._core.airport.Airport.SearchType # value = <SearchType.FULLNAME: 4>
        IATA: am4utils._core.airport.Airport.SearchType # value = <SearchType.IATA: 1>
        ICAO: am4utils._core.airport.Airport.SearchType # value = <SearchType.ICAO: 2>
        ID: am4utils._core.airport.Airport.SearchType # value = <SearchType.ID: 5>
        NAME: am4utils._core.airport.Airport.SearchType # value = <SearchType.NAME: 3>
        __members__: dict # value = {'ALL': <SearchType.ALL: 0>, 'IATA': <SearchType.IATA: 1>, 'ICAO': <SearchType.ICAO: 2>, 'NAME': <SearchType.NAME: 3>, 'FULLNAME': <SearchType.FULLNAME: 4>, 'ID': <SearchType.ID: 5>}
        pass
    class Suggestion():
        def __init__(self, arg0: Airport, arg1: float) -> None: ...
        @property
        def ap(self) -> Airport:
            """
            :type: Airport
            """
        @property
        def score(self) -> float:
            """
            :type: float
            """
        pass
    def __repr__(self) -> str: ...
    @staticmethod
    def search(s: str) -> Airport.SearchResult: ...
    @staticmethod
    def suggest(s: Airport.ParseResult) -> typing.List[Airport.Suggestion]: ...
    def to_dict(self) -> dict: ...
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
