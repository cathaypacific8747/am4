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

class AircraftSuggestionDict(BaseModel):
    aircraft: AircraftDict
    score: float

class AircraftResponse(BaseModel):
    status: str = Field("success", frozen=True)
    aircraft: AircraftDict

class AircraftNotFoundResponse(BaseModel):
    status: str = Field("not_found", frozen=True)
    parameter: str = Field("ac")
    suggestions: list[AircraftSuggestionDict]

class PaxConfigDict(BaseModel):
    y: int
    j: int
    f: int
    algorithm: Literal["FJY", "FYJ", "JFY", "JYF", "YFJ", "YJF", "NONE"]
    

class CargoConfigDict(BaseModel):
    l: int
    h: int
    algorithm: Literal["L", "H", "NONE"]

class PurchasedAircraftDict(AircraftDict):
    config: PaxConfigDict | CargoConfigDict