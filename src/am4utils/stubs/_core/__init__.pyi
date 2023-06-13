from __future__ import annotations
import am4utils._core
import typing

__all__ = [
    "AircraftType",
    "GameMode",
    "PaxConfigAlgorithm",
    "aircraft",
    "airport",
    "db",
    "route"
]


class AircraftType():
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
    CARGO: am4utils._core.AircraftType # value = <AircraftType.CARGO: 1>
    PAX: am4utils._core.AircraftType # value = <AircraftType.PAX: 0>
    VIP: am4utils._core.AircraftType # value = <AircraftType.VIP: 2>
    __members__: dict # value = {'PAX': <AircraftType.PAX: 0>, 'CARGO': <AircraftType.CARGO: 1>, 'VIP': <AircraftType.VIP: 2>}
    pass
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
    EASY: am4utils._core.GameMode # value = <GameMode.EASY: 0>
    REALISM: am4utils._core.GameMode # value = <GameMode.REALISM: 1>
    __members__: dict # value = {'EASY': <GameMode.EASY: 0>, 'REALISM': <GameMode.REALISM: 1>}
    pass
class PaxConfigAlgorithm():
    """
    Members:

      FJY

      FYJ

      JFY

      JYF

      YJF

      YFJ
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
    FJY: am4utils._core.PaxConfigAlgorithm # value = <PaxConfigAlgorithm.FJY: 0>
    FYJ: am4utils._core.PaxConfigAlgorithm # value = <PaxConfigAlgorithm.FYJ: 1>
    JFY: am4utils._core.PaxConfigAlgorithm # value = <PaxConfigAlgorithm.JFY: 2>
    JYF: am4utils._core.PaxConfigAlgorithm # value = <PaxConfigAlgorithm.JYF: 3>
    YFJ: am4utils._core.PaxConfigAlgorithm # value = <PaxConfigAlgorithm.YFJ: 5>
    YJF: am4utils._core.PaxConfigAlgorithm # value = <PaxConfigAlgorithm.YJF: 4>
    __members__: dict # value = {'FJY': <PaxConfigAlgorithm.FJY: 0>, 'FYJ': <PaxConfigAlgorithm.FYJ: 1>, 'JFY': <PaxConfigAlgorithm.JFY: 2>, 'JYF': <PaxConfigAlgorithm.JYF: 3>, 'YJF': <PaxConfigAlgorithm.YJF: 4>, 'YFJ': <PaxConfigAlgorithm.YFJ: 5>}
    pass
__version__ = '0.1.2'
