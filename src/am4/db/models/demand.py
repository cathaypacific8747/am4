from am4.utils.demand import CargoDemand, PaxDemand
from pydantic import BaseModel

from .util import assert_equal_property_names


class PyPaxDemand(BaseModel):
    y: int
    j: int
    f: int


class PyCargoDemand(BaseModel):
    l: int
    h: int


assert_equal_property_names(PaxDemand, PyPaxDemand)
assert_equal_property_names(CargoDemand, PyCargoDemand)
