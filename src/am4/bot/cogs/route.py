import discord
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.demand import CargoDemand
from am4.utils.route import AircraftRoute, Route
from discord.ext import commands
from discord.ext.commands.view import StringView

from ...common import HELP_AC_ARG0, HELP_AP_ARG0
from ...config import cfg
from ..converters import AircraftCvtr, AirportCvtr, CfgAlgCvtr, TPDCvtr
from ..errors import CustomErrHandler
from ..utils import COLOUR_GENERIC, IF, IH, IJ, IL, IY


class RouteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Finds information about a route",
        help=(
            "Finds information about an route given an origin and destination (and optionally the aircraft), examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}route HKG LHR\n"
            f"{cfg.bot.COMMAND_PREFIX}route id:3500 egll\n"
            f"{cfg.bot.COMMAND_PREFIX}route VHHH TPE dc910\n"
            "```"
        ),
        ignore_extra=False,
    )
    @commands.guild_only()
    async def route(
        self,
        ctx: commands.Context,
        ap0_query: Airport.SearchResult = commands.parameter(converter=AirportCvtr, description=HELP_AP_ARG0),
        ap1_query: Airport.SearchResult = commands.parameter(converter=AirportCvtr, description="Same as above"),
        ac_query: Aircraft.SearchResult | None = commands.parameter(
            converter=AircraftCvtr, default=None, description=HELP_AC_ARG0
        ),
        trips_per_day: tuple[int | None, AircraftRoute.Options.TPDMode] = commands.parameter(
            converter=TPDCvtr,
            default=TPDCvtr._default,
            displayed_default="AUTO",
            description="Trips per day and mode, ! = strict mode, multiple of by default, auto when not provided.",
        ),
        config_algorithm: Aircraft.PaxConfig.Algorithm | Aircraft.CargoConfig.Algorithm = commands.parameter(
            converter=CfgAlgCvtr,
            default=Aircraft.PaxConfig.Algorithm.AUTO,
            displayed_default="AUTO",
            description="Config algorithm (case insensitive)",
        ),
    ):
        if ac_query is None:
            r = Route.create(ap0_query.ap, ap1_query.ap)
            cargo_demand = CargoDemand(r.pax_demand)
            embed = discord.Embed(
                title=(
                    f"`╔ {ap0_query.ap.iata} `{ap0_query.ap.name}, {ap0_query.ap.country}\n"
                    f"`╚ {ap1_query.ap.iata} `{ap1_query.ap.name}, {ap1_query.ap.country}"
                ),
                description=(
                    f"** Demand**: {IY}`{r.pax_demand.y}` {IJ}`{r.pax_demand.j}` {IF}`{r.pax_demand.f}`\n"
                    f"**     **: {IL}`{cargo_demand.l}` {IH}`{cargo_demand.h}`\n"
                    f"**Distance**: {r.direct_distance:.3f} km (direct)"
                ),
                colour=COLOUR_GENERIC,
            )
            await ctx.send(embed=embed)
        else:
            # todo: swap default paxconfig.auto -> cargoconfig.auto
            await ctx.send(str(trips_per_day))

    @route.error
    async def route_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error)

        await h.invalid_airport("route")
        await h.missing_arg("route")
        await h.too_many_args("argument", "route")
        h.raise_for_unhandled()
