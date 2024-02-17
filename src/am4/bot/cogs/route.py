import math
import time
from typing import Literal

import discord
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.route import AircraftRoute, Route
from discord.ext import commands
from discord.ext.commands.view import StringView

from ...config import cfg
from ..converters import AircraftCvtr, AirportCvtr, CfgAlgCvtr, TPDCvtr
from ..errors import CustomErrHandler
from ..utils import COLOUR_GENERIC, HELP_CFG_ALG, HELP_TPD, fetch_user_info, format_config, format_demand, format_ticket

HELP_AP_ARG0 = "**Origin airport query**\nLearn more using `$help airport`."
HELP_AP_ARG1 = "**Destination airport query**\nLearn more using `$help airport`."
HELP_AC_ARG0 = "**Aircraft query**\nLearn more about how to customise engine/modifiers using `$help aircraft`."


class RouteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Finds information about a route",
        help=(
            "Finds information about an route given an origin and destination (and optionally the aircraft), examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}route hkg lhr\n"
            f"{cfg.bot.COMMAND_PREFIX}route id:3500 egll\n"
            f"{cfg.bot.COMMAND_PREFIX}route vhhh tpe dc910\n"
            f"{cfg.bot.COMMAND_PREFIX}route hkg yvr a388[sfc] 3\n"
            "```"
        ),
        ignore_extra=False,
    )
    @commands.guild_only()
    async def route(
        self,
        ctx: commands.Context,
        ap0_query: Airport.SearchResult = commands.parameter(converter=AirportCvtr, description=HELP_AP_ARG0),
        ap1_query: Airport.SearchResult = commands.parameter(converter=AirportCvtr, description=HELP_AP_ARG1),
        ac_query: Aircraft.SearchResult | None = commands.parameter(
            converter=AircraftCvtr, default=None, description=HELP_AC_ARG0
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
        if ac_query is None:
            r = Route.create(ap0_query.ap, ap1_query.ap)
            embed = discord.Embed(
                title=(
                    f"`╔ {ap0_query.ap.iata} `{ap0_query.ap.name}, {ap0_query.ap.country}\n"
                    f"`╚ {ap1_query.ap.iata} `{ap1_query.ap.name}, {ap1_query.ap.country}"
                ),
                description=(
                    f"** Demand**: {format_demand(r.pax_demand)}`\n"
                    f"**     ** {format_demand(r.pax_demand, as_cargo=True)}`\n"
                    f"**Distance**: {r.direct_distance:.3f} km (direct)"
                ),
                colour=COLOUR_GENERIC,
            )
            await ctx.send(embed=embed)
            return
        is_cargo = ac_query.ac.type == Aircraft.Type.CARGO
        tpd, tpd_mode = trips_per_day

        options = AircraftRoute.Options(trips_per_day=tpd, tpd_mode=tpd_mode, config_algorithm=config_algorithm)
        u, _ue = await fetch_user_info(ctx)

        acr = AircraftRoute.create(ap0_query.ap, ap1_query.ap, ac_query.ac, options, u)

        sa = acr.stopover.airport
        stopover_f = f"`╠ {sa.iata} `{sa.name}, {sa.country}\n" if acr.stopover.exists else ""
        distance_f = (
            f"{acr.stopover.full_distance:.3f} km (+{acr.stopover.full_distance-acr.route.direct_distance:.3f} km)"
            if acr.stopover.exists
            else f"{acr.route.direct_distance:.3f} km (direct)"
        )
        flight_time_f = time.strftime("%H:%M:%S", time.gmtime(acr.flight_time * 3600))
        ac_needed = math.ceil(acr.trips_per_day * acr.flight_time / 24)
        description = (
            f"**Flight Time**: {flight_time_f} ({acr.flight_time:.3f} hr)\n"
            f"**  Schedule**: {acr.trips_per_day:.0f} total trips/day: {ac_needed} A/C needed\n"
            f"**  Demand**: {format_demand(acr.route.pax_demand, is_cargo)}`\n"
            f"**  Config**: {format_config(acr.config)}`\n"
            f"**   Tickets**: {format_ticket(acr.ticket)}`\n"
            f"** Distance**: {distance_f}\n"
            f"**   Income**: $ {acr.income:,.0f}\n"
            f"**  -    Fuel**: $ {acr.fuel*u.fuel_price/1000:,.0f} ({acr.fuel:,.0f} lbs)\n"
            f"**  -     CO₂**: $ {acr.co2*u.co2_price/1000:,.0f} ({acr.co2:,.0f} quotas)\n"
            f"**  - Acheck**: $ {acr.acheck_cost:,.0f}\n"
            f"**  -   Repair**: $ {acr.repair_cost:,.0f}\n"
            f"**  =   Profit**: $ {acr.profit:,.0f}\n"
            f"**  Contrib**: $ {acr.contribution:.2f} (CI={acr.ci})\n"
        )
        embed = discord.Embed(
            title=(
                f"`╔ {ap0_query.ap.iata} `{ap0_query.ap.name}, {ap0_query.ap.country}\n{stopover_f}"
                f"`╚ {ap1_query.ap.iata} `{ap1_query.ap.name}, {ap1_query.ap.country}\n"
            ),
            description=description,
            colour=COLOUR_GENERIC,
        )
        await ctx.send(embed=embed)

    @route.error
    async def route_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error, "route")
        await h.invalid_airport()
        await h.invalid_aircraft()
        await h.invalid_tpd()
        await h.invalid_cfg_alg()
        await h.missing_arg()
        await h.too_many_args("argument")
        h.raise_for_unhandled()
