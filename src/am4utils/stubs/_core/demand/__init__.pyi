from __future__ import annotations
import am4utils._core.demand
import typing

__all__ = [
    "CargoDemand",
    "PaxDemand"
]


class CargoDemand():
    def __repr__(self) -> str: ...
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
    def __repr__(self) -> str: ...
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
