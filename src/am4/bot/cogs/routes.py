import asyncio
import math
import time
from concurrent.futures import ThreadPoolExecutor

import discord
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.game import User
from am4.utils.route import AircraftRoute, Destination, find_routes
from discord.ext import commands

from ...config import cfg
from ..cog import BaseCog
from ..converters import AircraftCvtr, AirportCvtr, CfgAlgCvtr, ConstraintCvtr, TPDCvtr
from ..errors import CustomErrHandler
from ..plots import mpl_map
from ..utils import (
    COLOUR_EASY,
    COLOUR_REALISM,
    COLOUR_WARNING,
    HELP_CFG_ALG,
    HELP_TPD,
    fetch_user_info,
    format_ap_short,
    format_config,
    format_demand,
    format_flight_time,
    format_modifiers,
    format_ticket,
)

HELP_AP = (
    f"**Origin airport query**\nThe IATA, ICAO, name or id.\nLearn more with `{cfg.bot.COMMAND_PREFIX}help airport`."
)
HELP_AC = (
    "**Aircraft query**\nThe short/full name of the aircraft (with custom engine/modifiers if necessary).\n"
    f"Learn more with `{cfg.bot.COMMAND_PREFIX}help aircraft`"
)
HELP_CONSTRAINT = (
    "**Constraint**\n"
    "- when not specified or given `NONE`, it'll optimise for max. profit per day per aircraft\n"
    "- if a constraint is given, it'll optimise for max. profit per trip\n"
    "  - by default, it'll be interpreted as distance in kilometres (i.e. `16000` will return routes < 16,000km)\n"
    "  - to constrain by flight time instead, use the `HH:MM`, `1d, HH:MM` or "
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
            "The simplest way to get started is:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}routes hkg a388\n"
            "```means: find the best routes departing `HKG` using `A380-800` (by highest profit per day per A/C).\n"
            "But as you may notice, the suggested routes may require you to *depart extremely frequently*. "
            "Say you would like to follow a schedule of departing 2x per day instead: ```php\n"
            f"{cfg.bot.COMMAND_PREFIX}routes hkg a388 12:00 2\n"
            "```means: also limit max flight time to 12:00 and have at least 2 departures per day per aircraft"
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
            displayed_default="NONE",
            description=HELP_CONSTRAINT,
        ),
        trips_per_day: tuple[int | None, AircraftRoute.Options.TPDMode] = commands.parameter(
            converter=TPDCvtr, default=TPDCvtr._default, displayed_default="AUTO", description=HELP_TPD
        ),
        config_algorithm: Aircraft.PaxConfig.Algorithm | Aircraft.CargoConfig.Algorithm = commands.parameter(
            converter=CfgAlgCvtr,
            default=CfgAlgCvtr._default,
            displayed_default="AUTO",
            description=HELP_CFG_ALG,
        ),
    ):
        is_cargo = ac_query.ac.type == Aircraft.Type.CARGO
        tpd, tpd_mode = trips_per_day
        max_distance, max_flight_time = constraint
        cons_set = constraint != ConstraintCvtr._default
        options = AircraftRoute.Options(
            **{
                k: v
                for k, v in {
                    "trips_per_day": tpd,
                    "tpd_mode": tpd_mode,
                    "config_algorithm": config_algorithm,
                    "max_distance": max_distance,
                    "max_flight_time": max_flight_time,
                    "sort_by": (
                        AircraftRoute.Options.SortBy.PER_AC_PER_DAY
                        if cons_set
                        else AircraftRoute.Options.SortBy.PER_TRIP
                    ),
                }.items()
                if v is not None
            }
        )

        # if the tpd is not provided, show generic warning of low tpd
        # otherwise, check if the constraint's equivalent flight time and tpd multiply to be <24.
        if cons_set:
            cons_eq_t = max_distance / ac_query.ac.speed if max_distance is not None else max_flight_time
            sugg_cons_t, sugg_tpd = 24 / tpd, math.floor(24 / cons_eq_t)
            if cons_eq_t * tpd > 24:
                cons_eq_f = ("equivalent to " if max_distance else "") + f"{cons_eq_t:.2f} hr"
                await ctx.send(
                    embed=discord.Embed(
                        title="Warning: Overconstrained!",
                        description=(
                            f"The constraint you have provided ({cons_eq_f}) means that one aircraft can fly "
                            f"at most {sugg_tpd:.0f} trips per day.\n"
                            f"More than one aircraft will be needed to satisfy the `{tpd}` trips per day per aircraft "
                            "you supplied, and will likely result in **poor profit per day per aircraft**.\n\n"
                            f"To fix this, reduce your trips per day per aircraft to `{sugg_tpd:.0f}`, or "
                            f"reduce your constraint to `{format_flight_time(sugg_cons_t, short=True)}` "
                            f"(`{ac_query.ac.speed * sugg_cons_t:.0f}` km)."
                        ),
                        color=COLOUR_WARNING,
                    )
                )

            if trips_per_day == TPDCvtr._default:
                await ctx.send(
                    embed=discord.Embed(
                        title="Warning: suboptimal routes incoming!",
                        description=(
                            "You did not set the trips per day per aircraft.\nThe bot will likely choose little"
                            "trips per day, and result in **poor profit per day per aircraft**.\n\n"
                            f"To fix this, specify the trips per day per aircraft (recommended: `{sugg_tpd}`)"
                        ),
                        color=COLOUR_WARNING,
                    )
                )

        u, _ue = await fetch_user_info(ctx)
        t_start = time.time()
        destinations = await self.get_routes(ap_query.ap, ac_query.ac, options, u)
        t_end = time.time()
        embed = discord.Embed(
            title=format_ap_short(ap_query.ap, mode=0),
            color=COLOUR_EASY if u.game_mode == User.GameMode.EASY else COLOUR_REALISM,
        )
        profits = []  # each entry represents one aircraft
        for i, d in enumerate(destinations):
            acr = d.ac_route

            profit_per_day_per_ac = acr.profit * acr.trips_per_day / acr.ac_needed
            for _ in range(acr.ac_needed):
                profits.append(profit_per_day_per_ac)
            if i > 2:
                continue

            stopover_f = f"{format_ap_short(acr.stopover.airport, mode=1)}\n" if acr.stopover.exists else ""
            distance_f = f"{acr.stopover.full_distance if acr.stopover.exists else acr.route.direct_distance:.0f} km"
            flight_time_f = format_flight_time(acr.flight_time)
            details_f = f"{acr.trips_per_day} t/d, {acr.ac_needed} ac"
            if acr.ac_needed > 1:
                details_f = f"**__{details_f}__**"
            embed.add_field(
                name=f"{stopover_f}{format_ap_short(d.airport, mode=2)}",
                value=(
                    f"**Demand**: {format_demand(acr.route.pax_demand, is_cargo)}\n"
                    f"**Config**: {format_config(acr.config)}\n"
                    f"**Tickets**: {format_ticket(acr.ticket)}\n"
                    f"**Details**: {distance_f} ({flight_time_f}), {details_f}, $ {acr.contribution:.1f} c/t\n"
                    f"**Profit**: $ {acr.profit:,.0f}/t, $ {profit_per_day_per_ac:,.0f}/d/ac\n"
                ),
                inline=False,
            )
        if not destinations:
            embed.description = (
                "There are no profitable routes found. Try relaxing the constraints or reducing the trips per day."
            )

        embed.set_footer(
            text=(
                f"{len(destinations)} routes found in {(t_end-t_start)*1000:.2f} ms\n"
                f"10 ac: $ {sum(profits[:10]):,.0f}/d, 30 ac: $ {sum(profits[:30]):,.0f}/d\n"
            ),
        )
        msg = await ctx.send(embed=embed)
        if not destinations:
            return

        im = mpl_map.plot_destinations(destinations, ap_query.ap.lng, ap_query.ap.lat, options.sort_by)
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
