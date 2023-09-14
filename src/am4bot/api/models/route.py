from typing import Literal, Optional
from pydantic import BaseModel, Field
from src.am4bot.api.models.aircraft import AircraftDict, PaxConfigDict, CargoConfigDict
from src.am4bot.api.models.airport import AirportDict
from src.am4bot.api.models.ticket import PaxTicketDict, CargoTicketDict, VIPTicketDict
from src.am4bot.api.models.demand import PaxDemandDict, CargoDemandDict

class RouteDict(BaseModel):
    pax_demand: PaxDemandDict
    cargo_demand: CargoDemandDict
    direct_distance: float

class RouteResponse(BaseModel):
    status: str = Field("success", frozen=True)
    ap_origin: AirportDict
    ap_destination: AirportDict
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
    config: Optional[PaxConfigDict | CargoConfigDict]
    trips_per_day: Optional[int]
    ticket: Optional[PaxTicketDict | CargoTicketDict | VIPTicketDict]
    max_income: Optional[float]
    income: Optional[float]
    fuel: Optional[float]
    co2: Optional[float]
    acheck_cost: Optional[float]
    repair_cost: Optional[float]
    profit: Optional[float]
    flight_time: Optional[float]
    needs_stopover: Optional[bool]
    profit: Optional[float]
    contribution: Optional[float]
    ci: Optional[int]
    stopover: Optional[StopoverDict | StopoverNonExistentDict]
    warnings: list[Literal["ERR_DISTANCE_ABOVE_SPECIFIED", "ERR_DISTANCE_TOO_LONG", "ERR_DISTANCE_TOO_SHORT", "REDUCED_CONTRIBUTION", "ERR_NO_STOPOVER", "ERR_FLIGHT_TIME_ABOVE_SPECIFIED", "ERR_INSUFFICIENT_DEMAND"]]

class ACRouteResponse(BaseModel):
    status: str = Field("success", frozen=True)
    ap_origin: AirportDict
    ap_destination: AirportDict
    ac: AircraftDict
    ac_route: ACRouteDict

class DestinationDict(BaseModel):
    airport: AirportDict
    ac_route: RouteDict

class ACRouteFindResponse(BaseModel):
    status: str = Field("success", frozen=True)
    destinations: list[DestinationDict]