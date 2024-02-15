from typing import Any

from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.route import AircraftRoute
from discord.ext import commands
from pydantic import BaseModel, ValidationError

from ..db.models.route import (
    PyACROptionsConfigAlgorithm,
    PyACROptionsMaxDistance,
    PyACROptionsMaxFlightTime,
    PyACROptionsTPDMode,
    PyACROptionsTripsPerDay,
)
from .errors import AircraftNotFoundError, AirportNotFoundError


class AirportCvtr(commands.Converter):
    async def convert(self, ctx: commands.Context, query: str) -> Airport.SearchResult:
        acsr = Airport.search(query)

        if not acsr.ap.valid:
            raise AirportNotFoundError(acsr)
        return acsr


class AircraftCvtr(commands.Converter):
    async def convert(self, ctx: commands.Context, query: str) -> Aircraft.SearchResult:
        acsr = Aircraft.search(query)

        if not acsr.ac.valid:
            raise AircraftNotFoundError(acsr)
        return acsr


class _ACROptions(BaseModel):
    algorithm: PyACROptionsConfigAlgorithm
    __max_distance: PyACROptionsMaxDistance
    __max_flight_time: PyACROptionsMaxFlightTime
    __tpd_mode: PyACROptionsTPDMode
    trips_per_day: PyACROptionsTripsPerDay


def acro_cast(k: str, v: Any) -> _ACROptions:
    return _ACROptions.__pydantic_validator__.validate_assignment(_ACROptions.model_construct(), k, v)


class TPDCvtr(commands.Converter):
    _default = (None, AircraftRoute.Options.TPDMode.AUTO)

    async def convert(self, ctx: commands.Context, tpdo: str) -> tuple[int | None, AircraftRoute.Options.TPDMode]:
        if tpdo is None or (tpd := tpdo.strip().lower()) == "auto":
            return self._default
        elif tpd.endswith("!"):
            try:
                return acro_cast("trips_per_day", tpd[:-1]).trips_per_day, AircraftRoute.Options.TPDMode.STRICT
            except ValidationError:
                raise commands.BadArgument("Invalid trips per day value")
        else:
            try:
                return acro_cast("trips_per_day", tpd).trips_per_day, AircraftRoute.Options.TPDMode.AUTO_MULTIPLE_OF
            except ValidationError:
                raise commands.BadArgument("Invalid trips per day value")


def to_core_enum() -> Aircraft.PaxConfig.Algorithm | Aircraft.CargoConfig.Algorithm:
    pass


class CfgAlgCvtr(commands.Converter):
    async def convert(
        self, ctx: commands.Context, alg: str
    ) -> Aircraft.PaxConfig.Algorithm | Aircraft.CargoConfig.Algorithm:
        ac: Aircraft.SearchResult = ctx.args[4]
        await ctx.send(str(ac.ac))
        try:
            alg_parsed = acro_cast("algorithm", alg.upper()).algorithm
        except ValidationError:
            raise commands.BadArgument("Invalid config algorithm")
        alg_core = (
            Aircraft.CargoConfig.Algorithm.__members__.get(alg_parsed)
            if ac.ac.type == Aircraft.Type.CARGO
            else Aircraft.PaxConfig.Algorithm.__members__.get(alg_parsed)
        )
        if alg_core is None:
            commands.BadArgument("Invalid config algorithm")
        await ctx.send(f"{alg=} {alg_parsed=} {ac.ac.type=} {alg_core=}")
        return alg_core
