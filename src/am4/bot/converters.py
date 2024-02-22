from datetime import timedelta
from typing import Annotated, Any, Literal

from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.route import AircraftRoute
from discord.ext import commands
from pydantic import BaseModel, Field
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
    ConstraintValidationError,
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
    max_distance: PyACROptionsMaxDistance
    max_flight_time: Annotated[timedelta, Field(ge=0, lt=72 * 3600)]
    __tpd_mode: PyACROptionsTPDMode
    trips_per_day: PyACROptionsTripsPerDay


class _SettingKeyCustom(BaseModel):
    training: Literal["max", "min"]


def acro_cast(k: str, v: Any) -> _ACROptions:
    return _ACROptions.__pydantic_validator__.validate_assignment(_ACROptions.model_construct(), k, v)


class SettingValueCvtr(commands.Converter):
    async def convert(self, ctx: commands.Context, value: Any) -> Any:
        key = ctx.args[-1]  # TODO: this is a hack, find a better way to get the key!
        model = _SettingKeyCustom if key == "training" else PyUser
        try:
            u_new = model.__pydantic_validator__.validate_assignment(model.model_construct(), key, value)
        except ValidationError as err:
            if key == "load":
                err.errors()[0]["msg"] += " Load factor is a percentage: if you want to set say 87%, use `87%`."
            raise SettingValueValidationError(err)
        v_new = getattr(u_new, key)
        return v_new


class TPDCvtr(commands.Converter):
    _default = (1, AircraftRoute.Options.TPDMode.AUTO)

    async def convert(self, ctx: commands.Context, tpdo: str) -> tuple[int | None, AircraftRoute.Options.TPDMode]:
        if tpdo is None or (tpd := tpdo.strip().lower()) == "auto":
            return self._default
        strict = tpd.endswith("!")
        try:
            return (
                acro_cast("trips_per_day", tpd[:-1] if strict else tpd).trips_per_day,
                AircraftRoute.Options.TPDMode.STRICT
                if strict
                else AircraftRoute.Options.TPDMode.STRICT_ALLOW_MULTIPLE_AC,
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

    @staticmethod
    async def _default(ctx: commands.Context) -> Aircraft.PaxConfig.Algorithm | Aircraft.CargoConfig.Algorithm:
        try:
            ac: Aircraft.SearchResult = next(a for a in ctx.args if isinstance(a, Aircraft.SearchResult))
        except StopIteration:
            # just to handle empty aircraft slots
            return Aircraft.PaxConfig.Algorithm.AUTO
        return (
            Aircraft.CargoConfig.Algorithm.AUTO
            if ac.ac.type == Aircraft.Type.CARGO
            else Aircraft.PaxConfig.Algorithm.AUTO
        )


class ConstraintCvtr(commands.Converter):
    _default = (None, None)

    def to_flight_time(self, constraint: str) -> float | None:
        try:
            time_parsed = acro_cast("max_flight_time", constraint).max_flight_time
            return time_parsed.total_seconds() / 3600
        except ValidationError as e:
            raise ConstraintValidationError(e)

    async def convert(self, ctx: commands.Context, constraint: str) -> tuple[float | None, float | None]:
        if constraint.strip().lower() == "none":
            return self._default
        try:
            dist_parsed = acro_cast("max_distance", constraint).max_distance
            return dist_parsed, None
        except ValidationError:
            return None, self.to_flight_time(constraint)
