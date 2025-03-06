from __future__ import annotations
import typing
__all__ = ['Airport']
class Airport:
    class ParseResult:
        def __init__(self, arg0: Airport.SearchType, arg1: str) -> None:
            ...
        @property
        def search_str(self) -> str:
            ...
        @property
        def search_type(self) -> Airport.SearchType:
            ...
    class SearchResult:
        def __init__(self, arg0: Airport, arg1: Airport.ParseResult) -> None:
            ...
        @property
        def ap(self) -> Airport:
            ...
        @property
        def parse_result(self) -> Airport.ParseResult:
            ...
    class SearchType:
        """
        Members:
        
          ALL
        
          IATA
        
          ICAO
        
          NAME
        
          FULLNAME
        
          ID
        """
        ALL: typing.ClassVar[Airport.SearchType]  # value = <SearchType.ALL: 0>
        FULLNAME: typing.ClassVar[Airport.SearchType]  # value = <SearchType.FULLNAME: 4>
        IATA: typing.ClassVar[Airport.SearchType]  # value = <SearchType.IATA: 1>
        ICAO: typing.ClassVar[Airport.SearchType]  # value = <SearchType.ICAO: 2>
        ID: typing.ClassVar[Airport.SearchType]  # value = <SearchType.ID: 5>
        NAME: typing.ClassVar[Airport.SearchType]  # value = <SearchType.NAME: 3>
        __members__: typing.ClassVar[dict[str, Airport.SearchType]]  # value = {'ALL': <SearchType.ALL: 0>, 'IATA': <SearchType.IATA: 1>, 'ICAO': <SearchType.ICAO: 2>, 'NAME': <SearchType.NAME: 3>, 'FULLNAME': <SearchType.FULLNAME: 4>, 'ID': <SearchType.ID: 5>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class Suggestion:
        def __init__(self, arg0: Airport, arg1: float) -> None:
            ...
        @property
        def ap(self) -> Airport:
            ...
        @property
        def score(self) -> float:
            ...
    @staticmethod
    def search(s: str) -> Airport.SearchResult:
        ...
    @staticmethod
    def suggest(s: Airport.ParseResult) -> list[Airport.Suggestion]:
        ...
    def __repr__(self) -> str:
        ...
    def to_dict(self) -> dict:
        ...
    @property
    def continent(self) -> str:
        ...
    @property
    def country(self) -> str:
        ...
    @property
    def fullname(self) -> str:
        ...
    @property
    def hub_cost(self) -> int:
        ...
    @property
    def iata(self) -> str:
        ...
    @property
    def icao(self) -> str:
        ...
    @property
    def id(self) -> int:
        ...
    @property
    def lat(self) -> float:
        ...
    @property
    def lng(self) -> float:
        ...
    @property
    def market(self) -> int:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def rwy(self) -> int:
        ...
    @property
    def rwy_codes(self) -> str:
        ...
    @property
    def valid(self) -> bool:
        ...
