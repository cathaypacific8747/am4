import discord
from am4.utils.airport import Airport
from discord.ext import commands

from ..common import HELP_AP_ARG0
from ..config import cfg
from .utils import COLOUR_ERROR, COLOUR_GENERIC, handle_too_many_args


class AirportCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Finds an airport",
        help=(
            "Finds information about an airport given a *query*, examples:```sh\n"
            f"{cfg.bot.COMMAND_PREFIX}airport HKG\n"
            f"{cfg.bot.COMMAND_PREFIX}airport id:3500\n"
            "```"
        ),
        ignore_extra=False,
    )
    @commands.guild_only()
    async def airport(self, ctx: commands.Context, query: str = commands.parameter(description=HELP_AP_ARG0)):
        ap = Airport.search(query)
        if ap.ap.valid:
            a = ap.ap
            e = discord.Embed(
                title=f"{a.name}, {a.country} (`{a.iata}` / `{a.icao}`)",
                description=(
                    f"**    Market**: {a.market}%\n"
                    f"**     Length**: {a.rwy} ft\n"
                    f"**    Coords**: {a.lat}, {a.lng}\n"
                    f"**Base Hub Cost**: ${a.hub_cost}\n"
                    f"**   Full Name**: {a.fullname}\n"
                    f"**  Continent**: {a.continent}\n"
                    f"**   Runways**: {a.rwy_codes}\n"
                    f"**      ID**: {a.id}\n"
                ),
                color=COLOUR_GENERIC,
            )
            await ctx.send(embed=e)
            return
        suggs = Airport.suggest(ap.parse_result)
        emb = sugg_embed(ap, suggs)
        if suggs:
            emb.add_field(
                name="Suggested command:", value=f"```sh\n{cfg.bot.COMMAND_PREFIX}airport {suggs[0].ap.icao}\n```"
            )
        await ctx.send(embed=emb)
        return

    @airport.error
    async def airport_error(self, ctx: commands.Context, error: commands.CommandError):
        await handle_too_many_args(ctx, error, "query", "airport")


def sugg_embed(ap: Airport.SearchResult, suggs: list[Airport.Suggestion]) -> discord.Embed:
    extra = f" using search mode `{st}`" if (st := ap.parse_result.search_type) != Airport.SearchType.ALL else ""
    embed = discord.Embed(
        title=f"Airport `{ap.parse_result.search_str}` not found{extra}!",
        color=COLOUR_ERROR,
    )
    if suggs:
        embed.add_field(
            name="Did you mean:",
            value="\n".join(f"- `{a.ap.iata}` / `{a.ap.icao}` ({a.ap.name}, {a.ap.country})" for a in suggs),
            inline=False,
        )
    return embed
