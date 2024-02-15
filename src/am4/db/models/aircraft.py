from typing import Literal

from am4.utils.aircraft import Aircraft
from pydantic import BaseModel

from .util import assert_equal_property_names

PyPaxConfigAlgorithm = Literal["AUTO", "FJY", "FYJ", "JFY", "JYF", "YFJ", "YJF"]


class PyPaxConfig(BaseModel):
    y: int
    j: int
    f: int
    algorithm: PyPaxConfigAlgorithm


PyCargoConfigAlgorithm = Literal["AUTO", "L", "H"]


class PyCargoConfig(BaseModel):
    l: int
    h: int
    algorithm: PyCargoConfigAlgorithm


PyConfigAlgorithmPax = Literal["AUTO", "FJY", "FYJ", "JFY", "JYF", "YFJ", "YJF"]
PyConfigAlgorithmCargo = Literal["AUTO", "L", "H"]


class PyAircraft(BaseModel):
    id: int
    shortname: str
    manufacturer: str
    name: str
    type: Literal["PAX", "CARGO", "VIP"]
    priority: int
    eid: int
    ename: str
    speed: float
    fuel: float
    co2: float
    cost: int
    capacity: int
    rwy: int
    check_cost: int
    range: int
    ceil: int
    maint: int
    pilots: int
    crew: int
    engineers: int
    technicians: int
    img: str
    wingspan: int
    length: int
    speed_mod: bool
    fuel_mod: bool
    co2_mod: bool
    fourx_mod: bool


class PyAircraftSuggestion(BaseModel):
    ac: PyAircraft
    score: float


assert_equal_property_names(Aircraft.PaxConfig, PyPaxConfig)
assert_equal_property_names(Aircraft.CargoConfig, PyCargoConfig)
assert_equal_property_names(Aircraft, PyAircraft)
assert_equal_property_names(Aircraft.Suggestion, PyAircraftSuggestion)
