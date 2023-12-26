import os
from typing import Annotated

import am4utils
from am4utils.aircraft import Aircraft
from am4utils.airport import Airport
from am4utils.game import User
from am4utils.route import AircraftRoute, Route, find_routes
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .dependencies import (
    # authenticate_user,
    # create_access_token,
    # oauth2_scheme,
    verify_user_token,
)
from .models.aircraft import AircraftNotFoundResponse, AircraftResponse
from .models.airport import AirportNotFoundResponse, AirportResponse
from .models.game import UserNotFoundResponse, UserResponse
from .models.route import (
    ACRouteFindResponse,
    ACRouteResponse,
    PyACROptionsConfigAlgorithm,
    PyACROptionsMaxDistance,
    PyACROptionsMaxFlightTime,
    PyACROptionsTPDMode,
    PyACROptionsTripsPerDay,
    RouteResponse,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["content-disposition", "set-cookie"]
)

# on startup
@app.on_event("startup")
async def startup():
    if (os.environ.get("PRODUCTION") == '1'):
        am4utils.db.init()
    else:
        am4utils.db.init(db_name='main')

ACSearchQuery = Annotated[str, Query(description="Search query for aircraft. Examples: `id:1`, `shortname:b744`, `name:B747-400`, `b744`, `B747-400`, `b744[1]`, `b744[1,sfc]`, `b744[3,s,f]`")]
APSearchQuery = Annotated[str, Query(description="Search query for airport. Examples: `id:3500`, `iata:Hkg`, `icao:vHHH`, `name:hong kong`, `VHHH`")]
class ACROptions():
    # not using pydantic basemodel: see https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#shortcut
    def __init__(
        self,
        config_algorithm: Annotated[PyACROptionsConfigAlgorithm, Query(description="[Optional] Aircraft configuration algorithm: one of `AUTO`, `FJY`, `FYJ`, `JFY`, `JYF`, `YFJ`, `YJF` for passenger aircraft, or `AUTO`, `L`, `H` for cargo aircraft - defaults to `AUTO` if not specified.")] = None,
        max_distance: Annotated[PyACROptionsMaxDistance, Query(description="[Optional] Maximum route distance (km) - defaults to 6371π if not specified.")] = None,
        max_flight_time: Annotated[PyACROptionsMaxFlightTime, Query(description="[Optional] Maximum flight time (h) - defaults to 24 if not specified.")] = None,
        tpd_mode: Annotated[PyACROptionsTPDMode, Query(description="[Optional] Trips per day mode: one of `AUTO`, `AUTO_MULTIPLE_OF`, `STRICT` - defaults to `AUTO` if not specified.")] = None,
        trips_per_day: Annotated[PyACROptionsTripsPerDay, Query(description="[Optional] Trips per day - defaults to 1 if not specified.")] = None,
    ):
        self.config_algorithm = config_algorithm
        self.max_distance = max_distance
        self.max_flight_time = max_flight_time
        self.tpd_mode = tpd_mode
        self.trips_per_day = trips_per_day
    
    def to_core(self, ac_type: Aircraft.Type) -> AircraftRoute.Options:
        opt = {}
        if self.config_algorithm is not None:
            alg = Aircraft.CargoConfig.Algorithm.__members__.get(self.config_algorithm) if ac_type == Aircraft.Type.CARGO else Aircraft.PaxConfig.Algorithm.__members__.get(self.config_algorithm)
            if alg is None:
                raise HTTPException(status_code=422, detail=[{
                    "loc": ["query", "config_algorithm"],
                    "msg": "Specified algorithm does not exist for this aircraft type",
                    "type": "value_error"
                }])
            opt["config_algorithm"] = alg
        if self.max_distance is not None:
            opt["max_distance"] = self.max_distance
        if self.max_flight_time is not None:
            opt["max_flight_time"] = self.max_flight_time
        if self.tpd_mode is not None:
            tpdm = AircraftRoute.Options.TPDMode.__members__.get(self.tpd_mode)
            if tpdm is None:
                raise HTTPException(status_code=422, detail=[{
                    "loc": ["query", "tpd_mode"],
                    "msg": "Specified trips per day mode does not exist",
                    "type": "value_error"
                }])
            opt["tpd_mode"] = tpdm
        if self.trips_per_day is not None:
            if opt.get("tpd_mode") == AircraftRoute.Options.TPDMode.AUTO or self.tpd_mode is None:
                kw = "explicitly specify" if self.tpd_mode is None else "use"
                raise HTTPException(status_code=422, detail=[{
                    "loc": ["query", "trips_per_day"],
                    "msg": f"Trips per day cannot be specified when `tpd_mode` is `AUTO`: {kw} `AUTO_MULTIPLE_OF` or `STRICT` instead",
                    "type": "value_error"
                }])
            opt["trips_per_day"] = self.trips_per_day
        return AircraftRoute.Options(**opt)
Realism = Annotated[bool, Query(description="[Optional] Whether to use realism mode - defaults to `false` if not specified.")]

def construct_acnf_response(param_name: str, ac_sugg: list[Aircraft.Suggestion]) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=404,
        content={
            "status": "not_found",
            "parameter": param_name,
            "suggestions": [
                {
                    "aircraft": a0s.ac.to_dict(),
                    "score": a0s.score
                } for a0s in ac_sugg
            ]
        }
    )
@app.get("/ac/search", response_model=AircraftResponse, responses={404: {"model": AircraftNotFoundResponse}})
async def ac_search(query: ACSearchQuery):
    ac = Aircraft.search(query)
    if ac.ac.valid:
        return {
            "status": "success",
            "aircraft": ac.ac.to_dict()
        }
    
    return construct_acnf_response("ac", Aircraft.suggest(ac.parse_result))



def construct_apnf_response(param_name: str, ap_sugg: list[Airport.Suggestion]) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=404,
        content={
            "status": "not_found",
            "parameter": param_name,
            "suggestions": [
                {
                    "airport": a0s.ap.to_dict(),
                    "score": a0s.score
                } for a0s in ap_sugg
            ]
        }
    )
@app.get("/ap/search", response_model=AirportResponse, responses={404: {"model": AirportNotFoundResponse}})
async def ap_search(query: APSearchQuery):
    ap = Airport.search(query)
    if ap.ap.valid:
        return {
            "status": "success",
            "airport": ap.ap.to_dict()
        }

    return construct_apnf_response("ap", Airport.suggest(ap.parse_result))



@app.get("/route/info", response_model=RouteResponse, responses={404: {"model": AirportNotFoundResponse}})
async def route_info(
    origin: APSearchQuery,
    destination: APSearchQuery,
):
    apsr0 = Airport.search(origin)
    if not apsr0.ap.valid:
        return construct_apnf_response("ap0", Airport.suggest(apsr0.parse_result))
    apsr1 = Airport.search(destination)
    if not apsr1.ap.valid:
        return construct_apnf_response("ap1", Airport.suggest(apsr1.parse_result))
    
    route = Route.create(apsr0.ap, apsr1.ap)
    return {
        "status": "success",
        "ap_origin": apsr0.ap.to_dict(),
        "ap_destination": apsr1.ap.to_dict(),
        "route": route.to_dict()
    }

@app.get("/ac_route/info", response_model=ACRouteResponse, response_model_exclude_unset=True, responses={404: {"model": AirportNotFoundResponse | AircraftNotFoundResponse}})
async def ac_route_info(
    origin: APSearchQuery,
    destination: APSearchQuery,
    ac: ACSearchQuery,
    options: Annotated[ACROptions, Depends()],
    realism: Realism = False
):
    apsr0 = Airport.search(origin)
    if not apsr0.ap.valid:
        return construct_apnf_response("ap0", Airport.suggest(apsr0.parse_result))
    apsr1 = Airport.search(destination)
    if not apsr1.ap.valid:
        return construct_apnf_response("ap1", Airport.suggest(apsr1.parse_result))
    acsr = Aircraft.search(ac)
    if not acsr.ac.valid:
        return construct_acnf_response("ac", Aircraft.suggest(acsr.parse_result))

    ac_route = AircraftRoute.create(
        apsr0.ap,
        apsr1.ap,
        acsr.ac,
        options.to_core(acsr.ac.type),
        User.Default(realism=True) if realism else User.Default()
    )
    return {
        "status": "success",
        "ap_origin": apsr0.ap.to_dict(),
        "ap_destination": apsr1.ap.to_dict(),
        "ac": acsr.ac.to_dict(),
        "ac_route": ac_route.to_dict(),
    }

@app.get("/ac_route/find", response_model=ACRouteFindResponse, responses={404: {"model": AirportNotFoundResponse | AircraftNotFoundResponse}})
async def ac_route_find_routes(
    ap0: APSearchQuery,
    ac: ACSearchQuery,
    options: Annotated[ACROptions, Depends()],
    realism: Realism = False
):
    apsr0 = Airport.search(ap0)
    if not apsr0.ap.valid:
        return construct_apnf_response("ap0", Airport.suggest(apsr0.parse_result))
    acsr = Aircraft.search(ac)
    if not acsr.ac.valid:
        return construct_acnf_response("ac", Aircraft.suggest(acsr.parse_result))
    
    destinations = find_routes(
        apsr0.ap,
        acsr.ac,
        options.to_core(acsr.ac.type),
        User.Default(realism=True) if realism else User.Default()
    )
    return ORJSONResponse(
        content={
            "status": "success",
            "destinations": [destination.to_dict() for destination in destinations]
        }
    )

@app.get("/users/me", response_model=UserResponse, responses={404: {"model": UserNotFoundResponse}})
async def user_me(
    user: Annotated[User, Depends(verify_user_token)]
):
    return ORJSONResponse(
        content={
            "status": "success",
            "user": user.to_dict()
        }
    )
