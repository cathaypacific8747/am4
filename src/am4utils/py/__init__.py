# workarounds for `import am4utils._core.aircraft` -> `import am4utils.aircraft`
# https://github.com/pybind/pybind11/issues/2639
# https://github.com/python/cpython/issues/87533
from ._core import aircraft, airport, db, demand, game, route, ticket

__all__ = [
    "aircraft",
    "airport",
    "db",
    "demand",
    "game",
    "route",
    "ticket"
]