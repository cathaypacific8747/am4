import discord
from am4.utils.airport import Airport
from discord.ext import commands

from ...common import HELP_AP_ARG0
from ...config import cfg
from ..base import BaseCog
from ..converters import AirportCvtr
from ..errors import CustomErrHandler
from ..utils import COLOUR_GENERIC


class AirportCog(BaseCog):
    @commands.command(
        brief="Finds an airport",
        help=(
            "Finds information about an airport given a *query*, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}airport HKG\n"
            f"{cfg.bot.COMMAND_PREFIX}airport id:3500\n"
            "```"
        ),
        ignore_extra=False,
    )
    @commands.guild_only()
    async def airport(
        self,
        ctx: commands.Context,
        ap_query: Airport.SearchResult = commands.parameter(converter=AirportCvtr, description=HELP_AP_ARG0),
    ):
        a = ap_query.ap
        e = discord.Embed(
            title=f"{a.name}, {a.country} (`{a.iata}` / `{a.icao}`)",
            description=(
                f"**    Market**: {a.market}%\n"
                f"**     Length**: {a.rwy} ft\n"
                f"**    Coords**: {a.lat}, {a.lng}\n"
                f"**Base Hub Cost**: ${a.hub_cost}\n"
                f"**   Full Name**: {a.fullname}\n"
                f"**  Continent**: {a.continent}\n"
                f"**   Runways**: {','.join(f'`{r}`' for r in a.rwy_codes.split('|'))}\n"
                f"**      ID**: {a.id}\n"
            ),
            color=COLOUR_GENERIC,
        )
        await ctx.send(embed=e)

    @airport.error
    async def airport_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error, "airport")

        await h.invalid_airport()
        await h.missing_arg()
        await h.too_many_args("ap_query")
        await h.raise_for_unhandled()
