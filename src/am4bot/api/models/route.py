from typing import Annotated, Literal, Optional

from am4utils.route import AircraftRoute, Route
from fastapi import Query
from pydantic import BaseModel, Field, confloat, conint

from .aircraft import (
    PyAircraft,
    PyCargoConfig,
    PyConfigAlgorithm,
    PyPaxConfig,
)
from .airport import PyAirport
from .demand import PyPaxDemand
from .ticket import PyCargoTicket, PyPaxTicket, PyVIPTicket
from .util import assert_equal_property_names


class PyRoute(BaseModel):
    pax_demand: PyPaxDemand
    direct_distance: float

assert_equal_property_names(Route, PyRoute)

class RouteResponse(BaseModel):
    status: str = Field("success", frozen=True)
    ap_origin: PyAirport
    ap_destination: PyAirport
    route: PyRoute

## ACR

PyACROptionsConfigAlgorithm = PyConfigAlgorithm
PyACROptionsMaxDistance = confloat(ge=0)
PyACROptionsMaxFlightTime = confloat(ge=0)
PyACROptionsTPDMode = Literal["AUTO", "AUTO_MULTIPLE_OF", "STRICT"]
PyACROptionsTripsPerDay = conint(ge=1)

class PyACRouteStopover(BaseModel):
    airport: PyAirport
    full_distance: float
    exists: Literal[True] = Field(True, frozen=True)

class PyACRouteStopoverNonExistent(BaseModel):
    exists: Literal[False] = Field(False, frozen=True)

class PyACRoute(BaseModel):
    route: PyRoute
    config: Optional[PyPaxConfig | PyCargoConfig] = None
    trips_per_day: Optional[int] = None
    ticket: Optional[PyPaxTicket | PyCargoTicket | PyVIPTicket] = None
    max_income: Optional[float] = None
    income: Optional[float] = None
    fuel: Optional[float] = None
    co2: Optional[float] = None
    acheck_cost: Optional[float] = None
    repair_cost: Optional[float] = None
    profit: Optional[float] = None
    flight_time: Optional[float] = None
    needs_stopover: Optional[bool] = None
    profit: Optional[float] = None
    contribution: Optional[float] = None
    ci: Optional[int] = None
    stopover: Optional[PyACRouteStopover | PyACRouteStopoverNonExistent] = None
    warnings: list[Literal["ERR_DISTANCE_ABOVE_SPECIFIED", "ERR_DISTANCE_TOO_LONG", "ERR_DISTANCE_TOO_SHORT", "REDUCED_CONTRIBUTION", "ERR_NO_STOPOVER", "ERR_FLIGHT_TIME_ABOVE_SPECIFIED", "ERR_INSUFFICIENT_DEMAND"]]
    valid: Optional[bool]

assert_equal_property_names(AircraftRoute.Stopover, PyACRouteStopover)
assert_equal_property_names(AircraftRoute, PyACRoute)

class ACRouteResponse(BaseModel):
    status: str = Field("success", frozen=True)
    ap_origin: PyAirport
    ap_destination: PyAirport
    ac: PyAircraft
    ac_route: PyACRoute

class Destination(BaseModel):
    airport: PyAirport
    ac_route: PyRoute

class ACRouteFindResponse(BaseModel):
    status: str = Field("success", frozen=True)
    destinations: list[Destination]
