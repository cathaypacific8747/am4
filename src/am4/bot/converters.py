from typing import Any

from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.route import AircraftRoute
from discord.ext import commands
from pydantic import BaseModel
from pydantic_core import ValidationError

from ..db.models.aircraft import PyConfigAlgorithmCargo, PyConfigAlgorithmPax
from ..db.models.game import PyUser
from ..db.models.route import (
    PyACROptionsMaxDistance,
    PyACROptionsMaxFlightTime,
    PyACROptionsTPDMode,
    PyACROptionsTripsPerDay,
)
from .errors import (
    AircraftNotFoundError,
    AirportNotFoundError,
    CfgAlgValidationError,
    SettingValueValidationError,
    TPDValidationError,
)


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
    algorithm_pax: PyConfigAlgorithmPax
    algorithm_cargo: PyConfigAlgorithmCargo
    __max_distance: PyACROptionsMaxDistance
    __max_flight_time: PyACROptionsMaxFlightTime
    __tpd_mode: PyACROptionsTPDMode
    trips_per_day: PyACROptionsTripsPerDay


def acro_cast(k: str, v: Any) -> _ACROptions:
    return _ACROptions.__pydantic_validator__.validate_assignment(_ACROptions.model_construct(), k, v)


class SettingValueCvtr(commands.Converter):
    async def convert(self, ctx: commands.Context, value: Any) -> Any:
        key = ctx.args[-1]
        print(ctx.args)
        try:
            u_new = PyUser.__pydantic_validator__.validate_assignment(PyUser.model_construct(), key, value)
        except ValidationError as err:
            raise SettingValueValidationError(err)
        v_new = getattr(u_new, key)
        return v_new


class TPDCvtr(commands.Converter):
    _default = (None, AircraftRoute.Options.TPDMode.AUTO)

    async def convert(self, ctx: commands.Context, tpdo: str) -> tuple[int | None, AircraftRoute.Options.TPDMode]:
        if tpdo is None or (tpd := tpdo.strip().lower()) == "auto":
            return self._default
        strict = tpd.endswith("!")
        try:
            return (
                acro_cast("trips_per_day", tpd[:-1] if strict else tpd).trips_per_day,
                AircraftRoute.Options.TPDMode.STRICT if strict else AircraftRoute.Options.TPDMode.AUTO_MULTIPLE_OF,
            )
        except ValidationError as e:
            raise TPDValidationError(e)


class CfgAlgCvtr(commands.Converter):
    async def convert(
        self, ctx: commands.Context, alg: str
    ) -> Aircraft.PaxConfig.Algorithm | Aircraft.CargoConfig.Algorithm:
        ac: Aircraft.SearchResult = next(a for a in ctx.args if isinstance(a, Aircraft.SearchResult))
        field_name = "algorithm_cargo" if ac.ac.type == Aircraft.Type.CARGO else "algorithm_pax"
        try:
            alg_parsed = getattr(acro_cast(field_name, alg.upper()), field_name)
        except ValidationError as e:
            raise CfgAlgValidationError(e)

        return (
            Aircraft.CargoConfig.Algorithm.__members__.get(alg_parsed)
            if ac.ac.type == Aircraft.Type.CARGO
            else Aircraft.PaxConfig.Algorithm.__members__.get(alg_parsed)
        )
