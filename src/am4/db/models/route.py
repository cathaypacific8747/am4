from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field

from am4.utils.route import AircraftRoute, Route

from .aircraft import (
    PyCargoConfig,
    PyConfigAlgorithmCargo,
    PyConfigAlgorithmPax,
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

## ACR

PyACROptionsConfigAlgorithm = Literal[PyConfigAlgorithmPax, PyConfigAlgorithmCargo]
PyACROptionsMaxDistance = Annotated[float, Field(gt=100, lt=65536)]
PyACROptionsMaxFlightTime = Annotated[float, Field(gt=0, lt=72)]
PyACROptionsTPDMode = Literal["AUTO", "STRICT_ALLOW_MULTIPLE_AC", "STRICT"]
PyACROptionsTripsPerDayPerAC = Annotated[int, Field(ge=1, lt=65536)]
PyACROptionsSortBy = Literal["PER_TRIP", "PER_AC_PER_DAY"]


class PyACRouteStopover(BaseModel):
    airport: PyAirport
    full_distance: float
    exists: Literal[True] = Field(True, frozen=True)


class PyACRouteStopoverNonExistent(BaseModel):
    exists: Literal[False] = Field(False, frozen=True)


class PyACRoute(BaseModel):
    route: PyRoute
    config: Optional[PyPaxConfig | PyCargoConfig] = None
    trips_per_day_per_ac: Optional[int] = None
    ticket: Optional[PyPaxTicket | PyCargoTicket | PyVIPTicket] = None
    max_income: Optional[float] = None
    income: Optional[float] = None
    fuel: Optional[float] = None
    co2: Optional[float] = None
    acheck_cost: Optional[float] = None
    repair_cost: Optional[float] = None
    profit: Optional[float] = None
    flight_time: Optional[float] = None
    num_ac: Optional[int] = None
    needs_stopover: Optional[bool] = None
    profit: Optional[float] = None
    contribution: Optional[float] = None
    ci: Optional[int] = None
    stopover: Optional[PyACRouteStopover | PyACRouteStopoverNonExistent] = None
    warnings: list[
        Literal[
            "ERR_DISTANCE_ABOVE_SPECIFIED",
            "ERR_DISTANCE_TOO_LONG",
            "ERR_DISTANCE_TOO_SHORT",
            "REDUCED_CONTRIBUTION",
            "ERR_NO_STOPOVER",
            "ERR_FLIGHT_TIME_ABOVE_SPECIFIED",
            "ERR_INSUFFICIENT_DEMAND",
            "ERR_TRIPS_PER_DAY_TOO_HIGH",
        ]
    ]
    valid: Optional[bool]
    max_tpd: Optional[int]


assert_equal_property_names(AircraftRoute.Stopover, PyACRouteStopover)
assert_equal_property_names(AircraftRoute, PyACRoute)
