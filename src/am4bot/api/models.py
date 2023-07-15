from typing import Literal
from pydantic import BaseModel, Field

class AircraftDict(BaseModel):
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

class AircraftSuggestion(BaseModel):
    aircraft: AircraftDict
    score: float

class AircraftResponse(BaseModel):
    status: str = Field("success", frozen=True)
    aircraft: AircraftDict

class AircraftNotFoundResponse(BaseModel):
    status: str = Field("not_found", frozen=True)
    parameter: str = Field("ac")
    suggestions: list[AircraftSuggestion]



class AirportDict(BaseModel):
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

class AirportSuggestion(BaseModel):
    airport: AirportDict
    score: float

class AirportResponse(BaseModel):
    status: str = Field("success", frozen=True)
    airport: AirportDict

class AirportNotFoundResponse(BaseModel):
    status: str = Field("not_found", frozen=True)
    parameter: str = Field("ap")
    suggestions: list[AirportSuggestion]


class PaxDemandDict(BaseModel):
    y: int
    j: int
    f: int

class CargoDemandDict(BaseModel):
    l: int
    h: int

class RouteDict(BaseModel):
    origin: AirportDict
    destination: AirportDict
    pax_demand: PaxDemandDict
    cargo_demand: CargoDemandDict
    direct_distance: float

class RouteResponse(BaseModel):
    status: str = Field("success", frozen=True)
    route: RouteDict