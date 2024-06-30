from typing import Annotated

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field

from am4.utils.aircraft import Aircraft
from am4.utils.game import User
from am4.utils.route import AircraftRoute

from ..common import (
    HELP_AC_ARG0,
    HELP_ACRO_CFG,
    HELP_ACRO_MAXDIST,
    HELP_ACRO_MAXFT,
    HELP_ACRO_TPD,
    HELP_ACRO_TPD_MODE,
    HELP_AP_ARG0,
    HELP_U_ACCUMULATED_COUNT,
    HELP_U_CO2_PRICE,
    HELP_U_CO2_TRAINING,
    HELP_U_FOURX,
    HELP_U_FUEL_PRICE,
    HELP_U_FUEL_TRAINING,
    HELP_U_H_TRAINING,
    HELP_U_INCOME_LOSS_TOL,
    HELP_U_L_TRAINING,
    HELP_U_LOAD,
    HELP_U_REPAIR_TRAINING,
    HELP_U_WEAR_TRAINING,
)
from ..db.models.aircraft import PyAircraft, PyAircraftSuggestion
from ..db.models.airport import PyAirport, PyAirportSuggestion
from ..db.models.game import PyUser
from ..db.models.route import (
    PyACROptionsConfigAlgorithm,
    PyACROptionsMaxDistance,
    PyACROptionsMaxFlightTime,
    PyACROptionsTPDMode,
    PyACROptionsTripsPerDayPerAC,
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
    Query(description=HELP_AC_ARG0),
]
FAPIReqAPSearchQuery = Annotated[
    str,
    Query(description=HELP_AP_ARG0),
]
FAPIReqRealism = Annotated[
    bool,
    Query(description="[Optional] **Whether to use realism mode** - defaults to `false` (easy) if not specified."),
]


# TODO: add sortby
class FAPIReqACROptions:
    # not using pydantic basemodel: see https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#shortcut
    def __init__(
        self,
        config_algorithm: Annotated[
            PyACROptionsConfigAlgorithm,
            Query(description=HELP_ACRO_CFG),
        ] = None,
        max_distance: Annotated[
            PyACROptionsMaxDistance,
            Query(description=HELP_ACRO_MAXDIST),
        ] = None,
        max_flight_time: Annotated[
            PyACROptionsMaxFlightTime,
            Query(description=HELP_ACRO_MAXFT),
        ] = None,
        tpd_mode: Annotated[
            PyACROptionsTPDMode,
            Query(description=HELP_ACRO_TPD_MODE),
        ] = None,
        trips_per_day_per_ac: Annotated[
            PyACROptionsTripsPerDayPerAC,
            Query(description=HELP_ACRO_TPD),
        ] = None,
    ):
        self.config_algorithm = config_algorithm
        self.max_distance = max_distance
        self.max_flight_time = max_flight_time
        self.tpd_mode = tpd_mode
        self.trips_per_day_per_ac = trips_per_day_per_ac

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
        if self.trips_per_day_per_ac is not None:
            if opt.get("tpd_mode") == AircraftRoute.Options.TPDMode.AUTO or self.tpd_mode is None:
                kw = "explicitly specify" if self.tpd_mode is None else "use"
                raise HTTPException(
                    status_code=422,
                    detail=[
                        {
                            "loc": ["query", "trips_per_day_per_ac"],
                            "msg": f"Trips per day cannot be specified when `tpd_mode` is `AUTO`: {kw} `STRICT_ALLOW_MULTIPLE_AC` or `STRICT` instead",
                            "type": "value_error",
                        }
                    ],
                )
            opt["trips_per_day_per_ac"] = self.trips_per_day_per_ac
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
                description=f"[Optional] {HELP_U_WEAR_TRAINING}",
                ge=0,
                le=5,
            ),
        ] = None,
        repair_training: Annotated[
            int,
            Query(
                description=f"[Optional] {HELP_U_REPAIR_TRAINING}",
                ge=0,
                le=5,
            ),
        ] = None,
        l_training: Annotated[
            int,
            Query(
                description=f"[Optional] {HELP_U_L_TRAINING}",
                ge=0,
                le=6,
            ),
        ] = None,
        h_training: Annotated[
            int,
            Query(
                description=f"[Optional] {HELP_U_H_TRAINING}",
                ge=0,
                le=6,
            ),
        ] = None,
        fuel_training: Annotated[
            int,
            Query(
                description=f"[Optional] {HELP_U_FUEL_TRAINING}",
                ge=0,
                le=3,
            ),
        ] = None,
        co2_training: Annotated[
            int,
            Query(
                description=f"[Optional] {HELP_U_CO2_TRAINING}",
                ge=0,
                le=5,
            ),
        ] = None,
        fuel_price: Annotated[
            int,
            Query(
                description=f"[Optional] {HELP_U_FUEL_PRICE}",
                ge=0,
                le=3000,
            ),
        ] = None,
        co2_price: Annotated[
            int,
            Query(
                description=f"[Optional] {HELP_U_CO2_PRICE}",
                ge=0,
                le=200,
            ),
        ] = None,
        accumulated_count: Annotated[
            int,
            Query(
                description=f"[Optional] {HELP_U_ACCUMULATED_COUNT}",
                ge=0,
                le=65535,
            ),
        ] = None,
        fourx: Annotated[
            bool,
            Query(description=f"[Optional] {HELP_U_FOURX}"),
        ] = None,
        income_loss_tol: Annotated[
            float,
            Query(
                description=f"[Optional] {HELP_U_INCOME_LOSS_TOL}",
                ge=0,
                le=1,
            ),
        ] = None,
        load: Annotated[
            float,
            Query(
                description=f"[Optional] {HELP_U_LOAD}",
                gt=0,
                le=1,
            ),
        ] = None,
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
            user.load = load

        return user
