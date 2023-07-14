from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import am4utils
from am4utils.aircraft import (
    Aircraft
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
    am4utils.db.init()

@app.get("/ac/search")
async def ac_search(search_str: str):
    a0 = Aircraft.search(search_str)
    if a0.ac.valid:
        return {
            "status": "success",
            "data": {
                "id": a0.ac.id,
                "manufacturer": a0.ac.manufacturer,
                "shortname": a0.ac.shortname,
                "name": a0.ac.name,
                # "type": a0.ac.type,
                "priority": a0.ac.priority,
                "eid": a0.ac.eid,
                "ename": a0.ac.ename,
                "speed": a0.ac.speed,
                "fuel": a0.ac.fuel,
                "co2": a0.ac.co2,
                "cost": a0.ac.cost,
                "capacity": a0.ac.capacity,
                "rwy": a0.ac.rwy,
                "check_cost": a0.ac.check_cost,
                "range": a0.ac.range,
                "ceil": a0.ac.ceil,
                "maint": a0.ac.maint,
                "pilots": a0.ac.pilots,
                "crew": a0.ac.crew,
                "engineers": a0.ac.engineers,
                "technicians": a0.ac.technicians,
                "img": a0.ac.img,
                "wingspan": a0.ac.wingspan,
                "length": a0.ac.length
            }
        }

    return {
        "status": "not_found",
        "data": {
            "suggestions": "not_implemented"
        }
    }