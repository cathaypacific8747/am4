from __future__ import annotations
import typing
__all__ = ['DatabaseException', 'init']
class DatabaseException(Exception):
    pass
def _debug_query(query: str) -> None:
    ...
def init(home_dir: str | None = None) -> None:
    ...
