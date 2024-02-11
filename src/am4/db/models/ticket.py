from am4.utils.ticket import CargoTicket, PaxTicket, VIPTicket
from pydantic import BaseModel

from .util import assert_equal_property_names


class PyPaxTicket(BaseModel):
    y: int
    j: int
    f: int


class PyCargoTicket(BaseModel):
    l: float
    h: float


class PyVIPTicket(BaseModel):
    y: int
    j: int
    f: int


assert_equal_property_names(PaxTicket, PyPaxTicket)
assert_equal_property_names(CargoTicket, PyCargoTicket)
assert_equal_property_names(VIPTicket, PyVIPTicket)
