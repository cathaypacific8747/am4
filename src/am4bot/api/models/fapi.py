from typing import Annotated

from am4utils.aircraft import Aircraft
from am4utils.game import User
from am4utils.route import AircraftRoute
from fastapi import HTTPException, Query
from pydantic import BaseModel, Field

from .aircraft import PyAircraft, PyAircraftSuggestion
from .airport import PyAirport, PyAirportSuggestion
from .game import PyUser
from .route import (
    PyACROptionsConfigAlgorithm,
    PyACROptionsMaxDistance,
    PyACROptionsMaxFlightTime,
    PyACROptionsTPDMode,
    PyACROptionsTripsPerDay,
    PyACRoute,
    PyRoute,
)


class FAPIRespAircraft(BaseModel):
    status: str = Field("success", frozen=True)
    aircraft: PyAircraft


class FAPIRespAircraftNotFound(BaseModel):
    status: str = Field("not_found", frozen=True)
    parameter: str = Field("ac")
    suggestions: list[PyAircraftSuggestion]


class FAPIRespAirport(BaseModel):
    status: str = Field("success", frozen=True)
    airport: PyAirport


class FAPIRespAirportNotFound(BaseModel):
    status: str = Field("not_found", frozen=True)
    parameter: str = Field("ap")
    suggestions: list[PyAirportSuggestion]


class FAPIToken(BaseModel):
    access_token: str
    token_type: str


class FAPIRespUser(BaseModel):
    status: str = Field("success", frozen=True)
    user: PyUser


class FAPIRespUserNotFound(BaseModel):
    status: str = Field("not_found", frozen=True)


class FAPIRespACRoute(BaseModel):
    status: str = Field("success", frozen=True)
    ap_origin: PyAirport
    ap_destination: PyAirport
    ac: PyAircraft
    ac_route: PyACRoute


class FAPIDestination(BaseModel):
    airport: PyAirport
    ac_route: PyRoute


class FAPIRespACRouteFind(BaseModel):
    status: str = Field("success", frozen=True)
    destinations: list[FAPIDestination]


class FAPIRespRoute(BaseModel):
    status: str = Field("success", frozen=True)
    ap_origin: PyAirport
    ap_destination: PyAirport
    route: PyRoute


FAPIReqACSearchQuery = Annotated[
    str,
    Query(
        description="""**Search query for aircraft** (case insensitive).
Examples: `b744`, `B747-400`, `id:1`, `shortname:b744`, `name:B747-400`, `b744[1]`, `b744[1,sfc]`, `b744[3,s,f,x]`.
Characters inside square brackets denote engine options: `s` for 1.1x **s**peed, `f` for 0.9x **f**uel, `c` for 0.9x **C**O2, `x` for 4**x** speed.
By default, the fastest engine option is used (priority 0) - for slower engine options, specify the engine option in the query.
"""
    ),
]
FAPIReqAPSearchQuery = Annotated[
    str,
    Query(
        description="""**Search query for airport** (case-insensitive).
Examples: `id:3500`, `iata:Hkg`, `icao:vHHH`, `name:hong kong`, `VHHH`"""
    ),
]
FAPIReqRealism = Annotated[
    bool,
    Query(
        description="[Optional] **Whether to use realism mode** - defaults to `false` (easy) if not specified."
    ),
]


class FAPIReqACROptions:
    # not using pydantic basemodel: see https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#shortcut
    def __init__(
        self,
        config_algorithm: Annotated[
            PyACROptionsConfigAlgorithm,
            Query(
                description="[Optional] **Aircraft configuration algorithm**: one of `AUTO`, `FJY`, `FYJ`, `JFY`, `JYF`, `YFJ`, `YJF` (pax/vip aircraft), or `AUTO`, `L`, `H` (cargo aircraft). If not specified, `AUTO` is used, which selects the best order for that distance class."
            ),
        ] = None,
        max_distance: Annotated[
            PyACROptionsMaxDistance,
            Query(
                description="[Optional] **Maximum route distance (km)** - defaults to 6371π if not specified."
            ),
        ] = None,
        max_flight_time: Annotated[
            PyACROptionsMaxFlightTime,
            Query(
                description="[Optional] **Maximum flight time (h)** - defaults to 24 if not specified."
            ),
        ] = None,
        tpd_mode: Annotated[
            PyACROptionsTPDMode,
            Query(
                description="[Optional] **Trips per day mode**: one of `AUTO`, `AUTO_MULTIPLE_OF`, `STRICT`. If not specified, `AUTO` is used, which finds the optimal trips_per_day through brute-forice."
            ),
        ] = None,
        trips_per_day: Annotated[
            PyACROptionsTripsPerDay,
            Query(
                description="[Optional] **Trips per day**: defaults to 1. Note that this parameter is only respected when tpd_mode is set to `AUTO_MULTIPLE_OF` or `STRICT`. When `tpd_mode=AUTO`, it throws an error."
            ),
        ] = None,
    ):
        self.config_algorithm = config_algorithm
        self.max_distance = max_distance
        self.max_flight_time = max_flight_time
        self.tpd_mode = tpd_mode
        self.trips_per_day = trips_per_day

    def to_core(self, ac_type: Aircraft.Type) -> AircraftRoute.Options:
        opt = {}
        if self.config_algorithm is not None:
            alg = (
                Aircraft.CargoConfig.Algorithm.__members__.get(self.config_algorithm)
                if ac_type == Aircraft.Type.CARGO
                else Aircraft.PaxConfig.Algorithm.__members__.get(self.config_algorithm)
            )
            if alg is None:
                raise HTTPException(
                    status_code=422,
                    detail=[
                        {
                            "loc": ["query", "config_algorithm"],
                            "msg": "Specified algorithm does not exist for this aircraft type",
                            "type": "value_error",
                        }
                    ],
                )
            opt["config_algorithm"] = alg
        if self.max_distance is not None:
            opt["max_distance"] = self.max_distance
        if self.max_flight_time is not None:
            opt["max_flight_time"] = self.max_flight_time
        if self.tpd_mode is not None:
            tpdm = AircraftRoute.Options.TPDMode.__members__.get(self.tpd_mode)
            if tpdm is None:
                raise HTTPException(
                    status_code=422,
                    detail=[
                        {
                            "loc": ["query", "tpd_mode"],
                            "msg": "Specified trips per day mode does not exist",
                            "type": "value_error",
                        }
                    ],
                )
            opt["tpd_mode"] = tpdm
        if self.trips_per_day is not None:
            if (
                opt.get("tpd_mode") == AircraftRoute.Options.TPDMode.AUTO
                or self.tpd_mode is None
            ):
                kw = "explicitly specify" if self.tpd_mode is None else "use"
                raise HTTPException(
                    status_code=422,
                    detail=[
                        {
                            "loc": ["query", "trips_per_day"],
                            "msg": f"Trips per day cannot be specified when `tpd_mode` is `AUTO`: {kw} `AUTO_MULTIPLE_OF` or `STRICT` instead",
                            "type": "value_error",
                        }
                    ],
                )
            opt["trips_per_day"] = self.trips_per_day
        return AircraftRoute.Options(**opt)


class FAPIReqUser:
    def __init__(
        self,
        # username: Annotated[str, Query(description="[Optional] Username")] = None,
        # game_id: Annotated[int, Query(description="[Optional] Game ID")] = None,
        # game_name: Annotated[str, Query(description="[Optional] Game name")] = None,
        # password: Annotated[str, Query(description="[Optional] Password")] = None,
        # discord_id: Annotated[int, Query(description="[Optional] Discord ID")] = None,
        realism: FAPIReqRealism = None,
        wear_training: Annotated[
            int,
            Query(
                description="[Optional] **Wear training** - defaults to `0` if not specified.",
                ge=0,
                le=5,
            ),
        ] = None,
        repair_training: Annotated[
            int,
            Query(
                description="[Optional] **Repair training** - defaults to `0` if not specified.",
                ge=0,
                le=5,
            ),
        ] = None,
        l_training: Annotated[
            int,
            Query(
                description="[Optional] **L training** - defaults to `0` if not specified.",
                ge=0,
                le=6,
            ),
        ] = None,
        h_training: Annotated[
            int,
            Query(
                description="[Optional] **H training** - defaults to `0` if not specified.",
                ge=0,
                le=6,
            ),
        ] = None,
        fuel_training: Annotated[
            int,
            Query(
                description="[Optional] **Fuel training** - defaults to `0` if not specified.",
                ge=0,
                le=3,
            ),
        ] = None,
        co2_training: Annotated[
            int,
            Query(
                description="[Optional] **CO2 training** - defaults to `0` if not specified.",
                ge=0,
                le=5,
            ),
        ] = None,
        fuel_price: Annotated[
            int,
            Query(
                description="[Optional] **Fuel price** - defaults to `700` if not specified.",
                ge=0,
                le=3000,
            ),
        ] = None,
        co2_price: Annotated[
            int,
            Query(
                description="[Optional] **CO2 price** - defaults to `120` if not specified.",
                ge=0,
                le=200,
            ),
        ] = None,
        accumulated_count: Annotated[
            int,
            Query(
                description="[Optional] **Accumulated fleet count**, used for marketing cost estimation - defaults to `0` if not specified.",
                ge=0,
                le=65535,
            ),
        ] = None,
        fourx: Annotated[
            bool,
            Query(
                description="[Optional] **4x** - defaults to `false` if not specified. *Note*: if this is set in the aircraft options (e.g. `a388[x]`), it will take precendence."
            ),
        ] = None,
        income_loss_tol: Annotated[
            float,
            Query(
                description="[Optional] **Income loss tolerance** - defaults to `0.0` if not specified. During end-game, hub availability becomes an issue and you might want to cram in more aircraft per route, even if that means losing some income. By default, the algorithm will stop increasing the trips/day as soon as the income drops below the maximum: setting this to `0.2` means that it'll continue inflating until the income is 80% of the max before moving onto the next candidate. Raising this value often yields much better income per hub.",
                ge=0,
                le=1,
            ),
        ] = None,
        load: Annotated[
            float,
            Query(
                description="[Optional] **Assumed aircraft load** - defaults to `0.87` if not specified (meaning 87% passenger filled: demand will be 'virtually' inflated by 1/0.87 = +14.9%.)",
                gt=0,
                le=1,
            ),
        ] = None,
        # role: Annotated[User.Role, Query(description="[Optional] Role - defaults to `USER` if not specified.)")] = None,
    ):
        self.realism = realism
        self.wear_training = wear_training
        self.repair_training = repair_training
        self.l_training = l_training
        self.h_training = h_training
        self.fuel_training = fuel_training
        self.co2_training = co2_training
        self.fuel_price = fuel_price
        self.co2_price = co2_price
        self.accumulated_count = accumulated_count
        self.fourx = fourx
        self.income_loss_tol = income_loss_tol
        self.load = load

    def to_core(self) -> User:
        user = User.Default(realism=True) if self.realism else User.Default()
        if (wt := self.wear_training) is not None:
            user.wear_training = wt
        if (rt := self.repair_training) is not None:
            user.repair_training = rt
        if (lt := self.l_training) is not None:
            user.l_training = lt
        if (ht := self.h_training) is not None:
            user.h_training = ht
        if (ft := self.fuel_training) is not None:
            user.fuel_training = ft
        if (ct := self.co2_training) is not None:
            user.co2_training = ct
        if (fp := self.fuel_price) is not None:
            user.fuel_price = fp
        if (cp := self.co2_price) is not None:
            user.co2_price = cp
        if (ac := self.accumulated_count) is not None:
            user.accumulated_count = ac
        if (fx := self.fourx) is not None:
            user.fourx = fx
        if (ilt := self.income_loss_tol) is not None:
            user.income_loss_tol = ilt
        if (load := self.load) is not None:
            user.set_load(load)

        return user
