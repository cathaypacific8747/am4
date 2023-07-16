from pydantic import BaseModel, Field

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