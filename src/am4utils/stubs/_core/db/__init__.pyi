from __future__ import annotations
import am4utils._core.db
import typing

__all__ = [
    "DatabaseException",
    "init"
]


class DatabaseException(Exception, BaseException):
    pass
def _debug_query(query: str) -> None:
    pass
def init(home_dir: typing.Optional[str] = None) -> None:
    pass
