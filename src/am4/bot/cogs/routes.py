import io

import discord
import orjson
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.route import AircraftRoute, Route, find_routes
from discord.ext import commands

from ...config import cfg
from ..cog import BaseCog
from ..converters import AircraftCvtr, AirportCvtr, CfgAlgCvtr, ConstraintCvtr, TPDCvtr
from ..errors import CustomErrHandler
from ..utils import COLOUR_GENERIC, HELP_CFG_ALG, HELP_TPD, fetch_user_info, format_config, format_demand, format_ticket

HELP_AP = "**Origin airport query**\nLearn more using `$help airport`."
HELP_AC = "**Aircraft query**\nLearn more about how to customise engine/modifiers using `$help aircraft`."
HELP_CONSTRAINT = (
    "**Constraint**\n"
    "- by default, the constraint is the distance in kilometres (e.g. `16000` will return routes < 16,000km)\n"
    "- to constrain by flight time instead, use the `HH:MM` or "
    "[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601#Durations) syntax"
)


class RoutesCog(BaseCog):
    @commands.command(
        brief="Searches best routes from a hub",
        help=(
            "Finds the most profitable destinations given an origin and aircraft, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}routes hkg a388 19000 3\n"
            f"{cfg.bot.COMMAND_PREFIX}routes vhhh b748f[sfc] 08:00\n"
            "```"
        ),
        ignore_extra=False,
    )
    @commands.guild_only()
    async def routes(
        self,
        ctx: commands.Context,
        ap_query: Airport.SearchResult = commands.parameter(converter=AirportCvtr, description=HELP_AP),
        ac_query: Aircraft.SearchResult = commands.parameter(converter=AircraftCvtr, description=HELP_AC),
        constraint: tuple[float | None, float | None] = commands.parameter(
            converter=ConstraintCvtr,
            default=ConstraintCvtr._default,
            displayed_default="20015",
            description=HELP_CONSTRAINT,
        ),
        trips_per_day: tuple[int | None, AircraftRoute.Options.TPDMode] = commands.parameter(
            converter=TPDCvtr, default=TPDCvtr._default, displayed_default="AUTO", description=HELP_TPD
        ),
        config_algorithm: Aircraft.PaxConfig.Algorithm | Aircraft.CargoConfig.Algorithm = commands.parameter(
            converter=CfgAlgCvtr,
            default=Aircraft.PaxConfig.Algorithm.AUTO,
            displayed_default="AUTO",
            description=HELP_CFG_ALG,
        ),
    ):
        is_cargo = ac_query.ac.type == Aircraft.Type.CARGO
        tpd, tpd_mode = trips_per_day
        max_distance, max_flight_time = constraint
        options = AircraftRoute.Options(
            **{
                k: v
                for k, v in {
                    "trips_per_day": tpd,
                    "tpd_mode": tpd_mode,
                    "config_algorithm": config_algorithm,
                    "max_distance": max_distance,
                    "max_flight_time": max_flight_time,
                }.items()
                if v is not None
            }
        )
        u, _ue = await fetch_user_info(ctx)
        destinations = find_routes(ap_query.ap, ac_query.ac, options, u)
        fp = io.BytesIO(
            orjson.dumps([destination.to_dict() for destination in destinations], option=orjson.OPT_INDENT_2)
        )

        storageInstance = await self.bot.get_channel(1208283378361573408).send(
            file=discord.File(fp, filename="routes.json")
        )

    @routes.error
    async def route_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error, "routes")
        await h.invalid_airport()
        await h.invalid_aircraft()
        await h.invalid_tpd()
        await h.invalid_cfg_alg()
        await h.invalid_constraint()
        await h.missing_arg()
        await h.too_many_args("argument")
        h.raise_for_unhandled()
