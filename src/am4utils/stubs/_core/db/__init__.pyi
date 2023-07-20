from __future__ import annotations
import am4utils._core.db
import typing

__all__ = [
    "DatabaseException",
    "init",
    "reset"
]


class DatabaseException(Exception, BaseException):
    pass
def _debug_query(query: str) -> None:
    pass
def init(home_dir: typing.Optional[str] = None, db_name: typing.Optional[str] = 'main') -> None:
    pass
def reset() -> None:
    pass
