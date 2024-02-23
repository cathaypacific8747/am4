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
            "```means: find the best routes departing `HKG` using `A380-800` (by highest profit per trip).\n"
            "But this does not guarantee the best profit *per day*. "
            "Say you would like to follow a schedule of departing 2x per day instead: ```php\n"
            f"{cfg.bot.COMMAND_PREFIX}routes hkg a388 12:00 2\n"
            "```means: limit max flight time to 12hrs and have at least 2 departures per day per aircraft"
            " (by highest profit per ac per day)."
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
        trips_per_day_per_ac: tuple[int | None, AircraftRoute.Options.TPDMode] = commands.parameter(
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
        tpd, tpd_mode = trips_per_day_per_ac
        max_distance, max_flight_time = constraint
        cons_set = constraint != ConstraintCvtr._default
        tpd_set = trips_per_day_per_ac != TPDCvtr._default
        options = AircraftRoute.Options(
            **{
                k: v
                for k, v in {
                    "trips_per_day_per_ac": tpd,
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
            # TODO: handle ranges!
            cons_eq_t = max_distance / ac_query.ac.speed if max_distance is not None else max_flight_time
            cons_eq_f = ("equivalent to " if max_distance else "") + f"max `{cons_eq_t:.2f}` hr"
            sugg_cons_t, sugg_tpd = 24 / tpd, math.floor(24 / cons_eq_t)
            if (t_ttl := cons_eq_t * tpd) > 24 and tpd_set:
                await ctx.send(
                    embed=discord.Embed(
                        title="Warning: Over-constrained!",
                        description=(
                            f"You have provided a constraint ({cons_eq_f}) and trips per day per A/C (`{tpd}`).\n"
                            f"But it is impossible to fly `{t_ttl:.2f}` hr in a day.\n"
                            f"I'll still respect your choice of `{tpd}` trips per day per A/C, but do note that the "
                            "suggested routes **may require you to depart very frequently**.\n\n"
                            f"To fix this, reduce your trips per day per A/C to `{sugg_tpd:.0f}`, or "
                            f"reduce your constraint to `{format_flight_time(sugg_cons_t, short=True)}` "
                            f"(`{ac_query.ac.speed * sugg_cons_t:.0f}` km)."
                        ),
                        color=COLOUR_WARNING,
                    )
                )
            elif t_ttl < 24 * 0.9 and tpd_set:
                sugg_tpd_f = f"increase your trips per day per A/C to `{sugg_tpd:.0f}`, or " if sugg_tpd != tpd else ""
                await ctx.send(
                    embed=discord.Embed(
                        title="Warning: Under-constrained!",
                        description=(
                            f"You have provided a constraint ({cons_eq_f}) and trips per day per A/C (`{tpd}`), "
                            f"meaning the average aircraft flies `{t_ttl:.2f}` hr in a day.\n"
                            "The profit per day per aircraft will be lower than the theoretical optimum.\n\n"
                            f"To fix this, {sugg_tpd_f}"
                            f"increase your constraint to `{format_flight_time(sugg_cons_t, short=True)}` "
                            f"(`{ac_query.ac.speed * sugg_cons_t:.0f}` km)."
                        ),
                        color=COLOUR_WARNING,
                    )
                )

            if not tpd_set:
                await ctx.send(
                    embed=discord.Embed(
                        title="Warning: Very short routes incoming!",
                        description=(
                            f"You have set a constraint ({cons_eq_f}), but did not set the trips per day per A/C.\n\n"
                            "I'll be sorting the routes by *max profit per day per A/C*, which will very likely "
                            "to be **extremely short routes**. You may not actually be able to depart that frequently, "
                            f"so I'd suggest you to specify the trips per day per aircraft (recommended: `{sugg_tpd}`)."
                            f"\n\nTip: Look at the tradeoff in the bottom right graph."
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

            profit_per_day_per_ac = acr.profit * acr.trips_per_day_per_ac
            for _ in range(acr.num_ac):
                profits.append(profit_per_day_per_ac)
            if i > 2:
                continue

            stopover_f = f"{format_ap_short(acr.stopover.airport, mode=1)}\n" if acr.stopover.exists else ""
            distance_f = f"{acr.stopover.full_distance if acr.stopover.exists else acr.route.direct_distance:.0f} km"
            flight_time_f = format_flight_time(acr.flight_time)
            details_f = f"{acr.trips_per_day_per_ac} t/d/ac × {acr.num_ac} ac"
            if acr.num_ac > 1:
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

        sorted_by = ", sorted by $ " + ("per ac per day" if cons_set else "per trip")
        embed.set_footer(
            text=(
                f"{len(destinations)} routes found in {(t_end-t_start)*1000:.2f} ms{sorted_by}\n"
                f"10 ac: $ {sum(profits[:10]):,.0f}/d, 30 ac: $ {sum(profits[:30]):,.0f}/d\n"
            ),
        )
        msg = await ctx.send(embed=embed)
        if not destinations:
            return

        im = mpl_map.plot_destinations(destinations, ap_query.ap.lng, ap_query.ap.lat)
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
