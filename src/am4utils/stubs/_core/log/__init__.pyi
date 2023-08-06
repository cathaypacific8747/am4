from __future__ import annotations
import am4utils._core.log
import typing
import datetime

__all__ = [
    "AllianceLog",
    "UserLog"
]


class AllianceLog():
    class Member():
        def __init__(self, id: int, username: str, joined: datetime.datetime, flights: int, contributed: int, daily_contribution: int, online: datetime.datetime, sv: float, season: int) -> None: ...
        @property
        def contributed(self) -> int:
            """
            :type: int
            """
        @property
        def daily_contribution(self) -> int:
            """
            :type: int
            """
        @property
        def flights(self) -> int:
            """
            :type: int
            """
        @property
        def id(self) -> int:
            """
            :type: int
            """
        @property
        def joined(self) -> datetime.datetime:
            """
            :type: datetime.datetime
            """
        @property
        def online(self) -> datetime.datetime:
            """
            :type: datetime.datetime
            """
        @property
        def season(self) -> int:
            """
            :type: int
            """
        @property
        def sv(self) -> float:
            """
            :type: float
            """
        @property
        def username(self) -> str:
            """
            :type: str
            """
        pass
    def __init__(self, id: int, name: str, rank: int, member_count: int, max_members: int, value: float, ipo: bool, min_sv: float, members: typing.List[AllianceLog.Member]) -> None: ...
    @staticmethod
    def from_log_id(log_id: str) -> AllianceLog: ...
    def insert_to_db(self) -> AllianceLog: ...
    @property
    def id(self) -> int:
        """
        :type: int
        """
    @property
    def ipo(self) -> bool:
        """
        :type: bool
        """
    @property
    def log_id(self) -> str:
        """
        :type: str
        """
    @property
    def log_time(self) -> datetime.datetime:
        """
        :type: datetime.datetime
        """
    @property
    def max_members(self) -> int:
        """
        :type: int
        """
    @property
    def member_count(self) -> int:
        """
        :type: int
        """
    @property
    def members(self) -> typing.List[AllianceLog.Member]:
        """
        :type: typing.List[AllianceLog.Member]
        """
    @property
    def min_sv(self) -> float:
        """
        :type: float
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def rank(self) -> int:
        """
        :type: int
        """
    @property
    def value(self) -> float:
        """
        :type: float
        """
    pass
class UserLog():
    class AircraftCount():
        @property
        def aircraft(self) -> str:
            """
            :type: str
            """
        @property
        def amount(self) -> int:
            """
            :type: int
            """
        pass
    class Award():
        def __init__(self, ts: datetime.datetime, award: str) -> None: ...
        @property
        def award(self) -> str:
            """
            :type: str
            """
        @property
        def ts(self) -> datetime.datetime:
            """
            :type: datetime.datetime
            """
        pass
    class RouteDetail():
        @property
        def arrived(self) -> datetime.datetime:
            """
            :type: datetime.datetime
            """
        @property
        def destination(self) -> str:
            """
            :type: str
            """
        @property
        def distance(self) -> int:
            """
            :type: int
            """
        @property
        def origin(self) -> str:
            """
            :type: str
            """
        @property
        def stopover(self) -> str:
            """
            :type: str
            """
        pass
    class Share():
        def __init__(self, ts: datetime.datetime, share: float) -> None: ...
        @property
        def share(self) -> float:
            """
            :type: float
            """
        @property
        def ts(self) -> datetime.datetime:
            """
            :type: datetime.datetime
            """
        pass
    def __init__(self, id: int, username: str, level: int, online: bool, share: float, shares_available: int, shares_sold: int, ipo: bool, fleet_count: int, routes: int, alliance: str, achievements: int, game_mode: bool, rank: int, reputation: int, cargo_reputation: int, founded: datetime.datetime, logo: str, share_log: typing.List[UserLog.Share], awards: typing.List[UserLog.Award], fleet: typing.List[UserLog.AircraftCount], route_list: typing.List[UserLog.RouteDetail]) -> None: ...
    @property
    def achievements(self) -> int:
        """
        :type: int
        """
    @property
    def alliance(self) -> str:
        """
        :type: str
        """
    @property
    def awards(self) -> typing.List[UserLog.Award]:
        """
        :type: typing.List[UserLog.Award]
        """
    @property
    def cargo_reputation(self) -> int:
        """
        :type: int
        """
    @property
    def fleet(self) -> typing.List[UserLog.AircraftCount]:
        """
        :type: typing.List[UserLog.AircraftCount]
        """
    @property
    def fleet_count(self) -> int:
        """
        :type: int
        """
    @property
    def founded(self) -> datetime.datetime:
        """
        :type: datetime.datetime
        """
    @property
    def game_mode(self) -> bool:
        """
        :type: bool
        """
    @property
    def ipo(self) -> bool:
        """
        :type: bool
        """
    @property
    def level(self) -> int:
        """
        :type: int
        """
    @property
    def log_id(self) -> str:
        """
        :type: str
        """
    @property
    def log_time(self) -> datetime.datetime:
        """
        :type: datetime.datetime
        """
    @property
    def logo(self) -> str:
        """
        :type: str
        """
    @property
    def online(self) -> bool:
        """
        :type: bool
        """
    @property
    def rank(self) -> int:
        """
        :type: int
        """
    @property
    def reputation(self) -> int:
        """
        :type: int
        """
    @property
    def route_list(self) -> typing.List[UserLog.RouteDetail]:
        """
        :type: typing.List[UserLog.RouteDetail]
        """
    @property
    def routes(self) -> int:
        """
        :type: int
        """
    @property
    def share(self) -> float:
        """
        :type: float
        """
    @property
    def share_log(self) -> typing.List[UserLog.Share]:
        """
        :type: typing.List[UserLog.Share]
        """
    @property
    def shares_available(self) -> int:
        """
        :type: int
        """
    @property
    def shares_sold(self) -> int:
        """
        :type: int
        """
    @property
    def username(self) -> str:
        """
        :type: str
        """
    pass
