from __future__ import annotations
import am4utils._core.user
import typing

__all__ = [
    "GameMode"
]


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
    EASY: am4utils._core.user.GameMode # value = <GameMode.EASY: 0>
    REALISM: am4utils._core.user.GameMode # value = <GameMode.REALISM: 1>
    __members__: dict # value = {'EASY': <GameMode.EASY: 0>, 'REALISM': <GameMode.REALISM: 1>}
    pass
