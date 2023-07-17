from typing import Literal
from pydantic import BaseModel, Field
from src.am4bot.api.models.aircraft import PurchasedAircraftDict
from src.am4bot.api.models.airport import AirportDict
from src.am4bot.api.models.ticket import PaxTicketDict, CargoTicketDict, VIPTicketDict
from src.am4bot.api.models.demand import PaxDemandDict, CargoDemandDict

class RouteDict(BaseModel):
    origin: AirportDict
    destination: AirportDict
    pax_demand: PaxDemandDict
    cargo_demand: CargoDemandDict
    direct_distance: float

class RouteResponse(BaseModel):
    status: str = Field("success", frozen=True)
    route: RouteDict

## ACR

class StopoverDict(BaseModel):
    airport: AirportDict
    full_distance: float
    exists: Literal[True] = Field(True, frozen=True)

class StopoverNonExistentDict(BaseModel):
    exists: Literal[False] = Field(False, frozen=True)

class ACRouteDict(BaseModel):
    route: RouteDict
    aircraft: PurchasedAircraftDict
    ticket: PaxTicketDict | CargoTicketDict | VIPTicketDict
    max_income: float
    income: float
    fuel: float
    co2: float
    needs_stopover: bool
    stopover: StopoverDict | StopoverNonExistentDict

class ACRouteResponse(BaseModel):
    status: str = Field("success", frozen=True)
    ac_route: ACRouteDict