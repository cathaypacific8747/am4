from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import am4utils
from am4utils.aircraft import Aircraft
from am4utils.airport import Airport
from am4utils.route import Route
from src.am4bot.api.models.aircraft import AircraftResponse, AircraftNotFoundResponse
from src.am4bot.api.models.airport import AirportResponse, AirportNotFoundResponse
from src.am4bot.api.models.route import RouteResponse, ACRouteResponse

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
    am4utils.db.init()



def construct_acnf_response(param_name: str, ac_sugg: list[Aircraft.Suggestion]) -> JSONResponse:
    return JSONResponse(
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
async def ac_search(query: str = Query(description="Search query for aircraft. Examples: `id:1`, `shortname:b744`, `name:B747-400`, `b744`, `B747-400`")):
    ac = Aircraft.search(query)
    if ac.ac.valid:
        return {
            "status": "success",
            "aircraft": ac.ac.to_dict()
        }
    
    return construct_acnf_response("ac", Aircraft.suggest(ac.parse_result))



def construct_apnf_response(param_name: str, ap_sugg: list[Airport.Suggestion]) -> JSONResponse:
    return JSONResponse(
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
async def ap_search(query: str = Query(description="Search query for airport. Examples: `id:3500`, `iata:Hkg`, `icao:vHHH`, `name:hong kong`, `VHHH`")):
    ap = Airport.search(query)
    if ap.ap.valid:
        return {
            "status": "success",
            "airport": ap.ap.to_dict()
        }

    return construct_apnf_response("ap", Airport.suggest(ap.parse_result))



@app.get("/route/info", response_model=RouteResponse, responses={404: {"model": AirportNotFoundResponse}})
async def route_info(
    ap0: str = Query(description="Origin airport"),
    ap1: str = Query(description="Destination airport"),
):
    apsr0 = Airport.search(ap0)
    if not apsr0.ap.valid:
        return construct_apnf_response("ap0", Airport.suggest(apsr0.parse_result))
    apsr1 = Airport.search(ap1)
    if not apsr1.ap.valid:
        return construct_apnf_response("ap1", Airport.suggest(apsr1.parse_result))
    
    route = Route.create(apsr0.ap, apsr1.ap)
    return {
        "status": "success",
        "route": route.to_dict()
    }

@app.get("/ac_route/info", response_model=ACRouteResponse, responses={404: {"model": AirportNotFoundResponse | AircraftNotFoundResponse}})
async def ac_route_info(
    ap0: str = Query(description="Origin airport"),
    ap1: str = Query(description="Destination airport"),
    ac: str = Query(description="Aircraft")
):
    apsr0 = Airport.search(ap0)
    if not apsr0.ap.valid:
        return construct_apnf_response("ap0", Airport.suggest(apsr0.parse_result))
    apsr1 = Airport.search(ap1)
    if not apsr1.ap.valid:
        return construct_apnf_response("ap1", Airport.suggest(apsr1.parse_result))
    acsr = Aircraft.search(ac)
    if not acsr.ac.valid:
        return construct_acnf_response("ac", Aircraft.suggest(acsr.parse_result))
    
    ac_route = Route.create(apsr0.ap, apsr1.ap).assign(acsr.ac)
    return {
        "status": "success",
        "ac_route": ac_route.to_dict(),
    }