from __future__ import annotations
import am4utils._core.demand
import typing

__all__ = [
    "CargoDemand",
    "PaxDemand"
]


class CargoDemand():
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, l: int, h: int) -> None: ...
    @typing.overload
    def __init__(self, pax_demand: PaxDemand) -> None: ...
    def __repr__(self) -> str: ...
    def to_dict(self) -> dict: ...
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
    pass
class PaxDemand():
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, y: int, j: int, f: int) -> None: ...
    def __repr__(self) -> str: ...
    def to_dict(self) -> dict: ...
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
