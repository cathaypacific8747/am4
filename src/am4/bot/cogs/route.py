import discord
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.route import Route
from discord.ext import commands
from discord.ext.commands.view import StringView

from ...common import HELP_AC_ARG0, HELP_AP_ARG0
from ...config import cfg
from ..converters import AircraftCvtr, AirportCvtr
from ..errors import CustomErrHandler
from ..utils import COLOUR_GENERIC


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
        # origin_ap: AirportCvtr = commands.parameter(description=HELP_AP_ARG0),
        # destination_ap: AirportCvtr = commands.parameter(description="Same as above"),
        ap0_query: Airport.SearchResult = commands.parameter(converter=AirportCvtr, description=HELP_AP_ARG0),
        ap1_query: Airport.SearchResult = commands.parameter(converter=AirportCvtr, description="Same as above"),
        ac_query: Aircraft.SearchResult | None = commands.parameter(
            converter=AircraftCvtr, default=None, description=HELP_AC_ARG0
        ),
    ):
        r = Route.create(ap0_query.ap, ap1_query.ap)
        await ctx.send(str(r.to_dict()))
        # e = discord.Embed(
        #     title=f"{a.name}, {a.country} (`{a.iata}` / `{a.icao}`)",
        #     description=(
        #         f"**    Market**: {a.market}%\n"
        #         f"**     Length**: {a.rwy} ft\n"
        #         f"**    Coords**: {a.lat}, {a.lng}\n"
        #         f"**Base Hub Cost**: ${a.hub_cost}\n"
        #         f"**   Full Name**: {a.fullname}\n"
        #         f"**  Continent**: {a.continent}\n"
        #         f"**   Runways**: {','.join(f'`{r}`' for r in a.rwy_codes.split('|'))}\n"
        #         f"**      ID**: {a.id}\n"
        #     ),
        #     color=COLOUR_GENERIC,
        # )
        # await ctx.send(embed=e)

    @route.error
    async def route_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error)

        await h.invalid_airport("route")
        await h.missing_arg("route")
        await h.too_many_args("argument", "route")
        h.raise_for_unhandled()
