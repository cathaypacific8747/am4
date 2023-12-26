from am4utils.airport import Airport
from pydantic import BaseModel, Field

from .util import assert_equal_property_names


class PyAirport(BaseModel):
    id: int
    name: str
    fullname: str
    country: str
    continent: str
    iata: str
    icao: str
    lat: float
    lng: float
    rwy: int
    market: int
    hub_cost: int
    rwy_codes: str # TODO: split by |

class PyAirportSuggestion(BaseModel):
    ap: PyAirport
    score: float

assert_equal_property_names(Airport, PyAirport)
assert_equal_property_names(Airport.Suggestion, PyAirportSuggestion)

class AirportResponse(BaseModel):
    status: str = Field("success", frozen=True)
    airport: PyAirport

class AirportNotFoundResponse(BaseModel):
    status: str = Field("not_found", frozen=True)
    parameter: str = Field("ap")
    suggestions: list[PyAirportSuggestion]
