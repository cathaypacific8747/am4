from __future__ import annotations
import am4utils._core.game
import typing

__all__ = [
    "Campaign",
    "User"
]


class Campaign():
    class Airline():
        """
        Members:

          C4_4HR

          C4_8HR

          C4_12HR

          C4_16HR

          C4_20HR

          C4_24HR

          C3_4HR

          C3_8HR

          C3_12HR

          C3_16HR

          C3_20HR

          C3_24HR

          C2_4HR

          C2_8HR

          C2_12HR

          C2_16HR

          C2_20HR

          C2_24HR

          C1_4HR

          C1_8HR

          C1_12HR

          C1_16HR

          C1_20HR

          C1_24HR

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
        C1_12HR: am4utils._core.game.Campaign.Airline # value = <Airline.C1_12HR: 13>
        C1_16HR: am4utils._core.game.Campaign.Airline # value = <Airline.C1_16HR: 14>
        C1_20HR: am4utils._core.game.Campaign.Airline # value = <Airline.C1_20HR: 15>
        C1_24HR: am4utils._core.game.Campaign.Airline # value = <Airline.C1_24HR: 16>
        C1_4HR: am4utils._core.game.Campaign.Airline # value = <Airline.C1_4HR: 11>
        C1_8HR: am4utils._core.game.Campaign.Airline # value = <Airline.C1_8HR: 12>
        C2_12HR: am4utils._core.game.Campaign.Airline # value = <Airline.C2_12HR: 23>
        C2_16HR: am4utils._core.game.Campaign.Airline # value = <Airline.C2_16HR: 24>
        C2_20HR: am4utils._core.game.Campaign.Airline # value = <Airline.C2_20HR: 25>
        C2_24HR: am4utils._core.game.Campaign.Airline # value = <Airline.C2_24HR: 26>
        C2_4HR: am4utils._core.game.Campaign.Airline # value = <Airline.C2_4HR: 21>
        C2_8HR: am4utils._core.game.Campaign.Airline # value = <Airline.C2_8HR: 22>
        C3_12HR: am4utils._core.game.Campaign.Airline # value = <Airline.C3_12HR: 33>
        C3_16HR: am4utils._core.game.Campaign.Airline # value = <Airline.C3_16HR: 34>
        C3_20HR: am4utils._core.game.Campaign.Airline # value = <Airline.C3_20HR: 35>
        C3_24HR: am4utils._core.game.Campaign.Airline # value = <Airline.C3_24HR: 36>
        C3_4HR: am4utils._core.game.Campaign.Airline # value = <Airline.C3_4HR: 31>
        C3_8HR: am4utils._core.game.Campaign.Airline # value = <Airline.C3_8HR: 32>
        C4_12HR: am4utils._core.game.Campaign.Airline # value = <Airline.C4_12HR: 43>
        C4_16HR: am4utils._core.game.Campaign.Airline # value = <Airline.C4_16HR: 44>
        C4_20HR: am4utils._core.game.Campaign.Airline # value = <Airline.C4_20HR: 45>
        C4_24HR: am4utils._core.game.Campaign.Airline # value = <Airline.C4_24HR: 46>
        C4_4HR: am4utils._core.game.Campaign.Airline # value = <Airline.C4_4HR: 41>
        C4_8HR: am4utils._core.game.Campaign.Airline # value = <Airline.C4_8HR: 42>
        NONE: am4utils._core.game.Campaign.Airline # value = <Airline.NONE: 0>
        __members__: dict # value = {'C4_4HR': <Airline.C4_4HR: 41>, 'C4_8HR': <Airline.C4_8HR: 42>, 'C4_12HR': <Airline.C4_12HR: 43>, 'C4_16HR': <Airline.C4_16HR: 44>, 'C4_20HR': <Airline.C4_20HR: 45>, 'C4_24HR': <Airline.C4_24HR: 46>, 'C3_4HR': <Airline.C3_4HR: 31>, 'C3_8HR': <Airline.C3_8HR: 32>, 'C3_12HR': <Airline.C3_12HR: 33>, 'C3_16HR': <Airline.C3_16HR: 34>, 'C3_20HR': <Airline.C3_20HR: 35>, 'C3_24HR': <Airline.C3_24HR: 36>, 'C2_4HR': <Airline.C2_4HR: 21>, 'C2_8HR': <Airline.C2_8HR: 22>, 'C2_12HR': <Airline.C2_12HR: 23>, 'C2_16HR': <Airline.C2_16HR: 24>, 'C2_20HR': <Airline.C2_20HR: 25>, 'C2_24HR': <Airline.C2_24HR: 26>, 'C1_4HR': <Airline.C1_4HR: 11>, 'C1_8HR': <Airline.C1_8HR: 12>, 'C1_12HR': <Airline.C1_12HR: 13>, 'C1_16HR': <Airline.C1_16HR: 14>, 'C1_20HR': <Airline.C1_20HR: 15>, 'C1_24HR': <Airline.C1_24HR: 16>, 'NONE': <Airline.NONE: 0>}
        pass
    class Eco():
        """
        Members:

          C_4HR

          C_8HR

          C_12HR

          C_16HR

          C_20HR

          C_24HR

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
        C_12HR: am4utils._core.game.Campaign.Eco # value = <Eco.C_12HR: 53>
        C_16HR: am4utils._core.game.Campaign.Eco # value = <Eco.C_16HR: 54>
        C_20HR: am4utils._core.game.Campaign.Eco # value = <Eco.C_20HR: 55>
        C_24HR: am4utils._core.game.Campaign.Eco # value = <Eco.C_24HR: 56>
        C_4HR: am4utils._core.game.Campaign.Eco # value = <Eco.C_4HR: 51>
        C_8HR: am4utils._core.game.Campaign.Eco # value = <Eco.C_8HR: 52>
        NONE: am4utils._core.game.Campaign.Eco # value = <Eco.NONE: 0>
        __members__: dict # value = {'C_4HR': <Eco.C_4HR: 51>, 'C_8HR': <Eco.C_8HR: 52>, 'C_12HR': <Eco.C_12HR: 53>, 'C_16HR': <Eco.C_16HR: 54>, 'C_20HR': <Eco.C_20HR: 55>, 'C_24HR': <Eco.C_24HR: 56>, 'NONE': <Eco.NONE: 0>}
        pass
    @staticmethod
    def Default() -> Campaign: ...
    def estimate_cargo_reputation(self, base_reputation: float = 45) -> float: ...
    def estimate_pax_reputation(self, base_reputation: float = 45) -> float: ...
    @staticmethod
    def parse(s: str) -> Campaign: ...
    @property
    def cargo_activated(self) -> Campaign.Airline:
        """
        :type: Campaign.Airline
        """
    @property
    def eco_activated(self) -> Campaign.Eco:
        """
        :type: Campaign.Eco
        """
    @property
    def pax_activated(self) -> Campaign.Airline:
        """
        :type: Campaign.Airline
        """
    pass
class User():
    class GameMode():
        """
        Members:

          EASY

          REALISM
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
        EASY: am4utils._core.game.User.GameMode # value = <GameMode.EASY: 0>
        REALISM: am4utils._core.game.User.GameMode # value = <GameMode.REALISM: 1>
        __members__: dict # value = {'EASY': <GameMode.EASY: 0>, 'REALISM': <GameMode.REALISM: 1>}
        pass
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def co2_price(self) -> int:
        """
        :type: int
        """
    @property
    def co2_training(self) -> int:
        """
        :type: int
        """
    @property
    def fuel_price(self) -> int:
        """
        :type: int
        """
    @property
    def fuel_training(self) -> int:
        """
        :type: int
        """
    @property
    def game_id(self) -> int:
        """
        :type: int
        """
    @property
    def game_mode(self) -> User.GameMode:
        """
        :type: User.GameMode
        """
    @property
    def h_training(self) -> int:
        """
        :type: int
        """
    @property
    def id(self) -> int:
        """
        :type: int
        """
    @property
    def ign(self) -> str:
        """
        :type: str
        """
    @property
    def l_training(self) -> int:
        """
        :type: int
        """
    @property
    def load(self) -> float:
        """
        :type: float
        """
    pass
