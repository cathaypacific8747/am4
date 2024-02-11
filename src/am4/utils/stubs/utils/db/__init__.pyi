from __future__ import annotations
import typing
from . import utils
__all__ = ['DatabaseException', 'init', 'utils']
class DatabaseException(Exception):
    pass
def _debug_query(query: str) -> None:
    ...
def init(home_dir: str | None = None) -> None:
    ...
