import asyncio
import io
import math
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

import discord
import matplotlib.pyplot as plt
import orjson
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.game import User
from am4.utils.route import AircraftRoute, Destination, find_routes
from discord.ext import commands

from ...config import cfg
from ..cog import BaseCog
from ..converters import AircraftCvtr, AirportCvtr, CfgAlgCvtr, ConstraintCvtr, TPDCvtr
from ..errors import CustomErrHandler
from ..plots import DestinationData, mpl_map
from ..utils import (
    COLOUR_EASY,
    COLOUR_GENERIC,
    COLOUR_REALISM,
    HELP_CFG_ALG,
    HELP_TPD,
    fetch_user_info,
    format_ap_short,
    format_config,
    format_demand,
    format_modifiers,
    format_ticket,
)

HELP_AP = "**Origin airport query**\nLearn more using `$help airport`."
HELP_AC = "**Aircraft query**\nLearn more about how to customise engine/modifiers using `$help aircraft`."
HELP_CONSTRAINT = (
    "**Constraint**\n"
    "- by default, the constraint is the distance in kilometres (e.g. `16000` will return routes < 16,000km)\n"
    "- to constrain by flight time instead, use the `HH:MM` or "
    "[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601#Durations) syntax"
)


class RoutesCog(BaseCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def get_routes(self, *args) -> list[Destination]:
        return await asyncio.get_event_loop().run_in_executor(self.executor, find_routes, *args)

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
        t_start = time.time()
        destinations = await self.get_routes(ap_query.ap, ac_query.ac, options, u)
        t_end = time.time()
        embed = discord.Embed(
            title=format_ap_short(ap_query.ap, mode=0),
            color=COLOUR_EASY if u.game_mode == User.GameMode.EASY else COLOUR_REALISM,
        )
        labels = []
        lats, lngs = [], []
        profits, acns = [], []
        for i, d in enumerate(destinations):
            acr = d.ac_route
            ac_needed = math.ceil(acr.trips_per_day * acr.flight_time / 24)

            labels.append(d.airport.iata)
            profits.append(acr.profit)
            acns.append(ac_needed)
            lats.append(d.airport.lat)
            lngs.append(d.airport.lng)
            if i > 2:
                continue

            stopover_f = f"{format_ap_short(acr.stopover.airport, mode=1)}\n" if acr.stopover.exists else ""
            distance_f = f"{acr.stopover.full_distance if acr.stopover.exists else acr.route.direct_distance:.0f} km"
            flight_time_f = time.strftime("%H:%M", time.gmtime(acr.flight_time * 3600))
            details_f = f"{acr.trips_per_day} t/d, {ac_needed} ac"
            if ac_needed > 1:
                details_f = f"**__{details_f}__**"
            embed.add_field(
                name=f"{stopover_f}{format_ap_short(d.airport, mode=2)}",
                value=(
                    f"**Demand**: {format_demand(acr.route.pax_demand, is_cargo)}\n"
                    f"**Config**: {format_config(acr.config)}\n"
                    f"**Tickets**: {format_ticket(acr.ticket)}\n"
                    f"**Details**: {distance_f} ({flight_time_f}), {details_f}, {acr.contribution:.2f} c/f\n"
                    f"**Profit**: $ {acr.profit:,.0f}/t/ac, $ {acr.profit * acr.trips_per_day / ac_needed:,.0f}/d/ac\n"
                ),
                inline=False,
            )

        top_10 = sum(profits[:10])
        top_30 = sum(profits[:30])
        embed.set_footer(
            text=(
                f"{len(destinations)} routes found in {(t_end-t_start)*1000:.2f} ms\n"
                f"top-10: $ {top_10:,.0f}/d, top-30: $ {top_30:,.0f}/d\n"
                f"{ac_query.ac.name}/{ac_query.ac.ename}{format_modifiers(ac_query.ac)}, CI: {acr.ci}\n"
            ),
        )
        msg = await ctx.send(embed=embed)

        im = mpl_map.plot_destinations(DestinationData(lngs, lats, profits, acns, ap_query.ap.lng, ap_query.ap.lat))
        file = discord.File(im, filename="routes.png")
        embed.set_image(url="attachment://routes.png")
        await msg.edit(embed=embed, attachments=[file])

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
