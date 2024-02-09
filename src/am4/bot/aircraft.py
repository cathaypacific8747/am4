import discord
from am4.utils.aircraft import Aircraft
from discord.ext import commands

from ..common import HELP_AC_ARG0
from ..config import cfg
from .utils import COLOUR_ERROR, COLOUR_GENERIC, handle_too_many_args


class AircraftCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Finds an aircraft",
        help=(
            "Finds information about an aircraft given a *query*, examples:```sh\n"
            f"{cfg.bot.COMMAND_PREFIX}aircraft a388\n"
            f"{cfg.bot.COMMAND_PREFIX}aircraft b744[2]\n"
            f'{cfg.bot.COMMAND_PREFIX}aircraft "ATR 42-300[sfcx]"\n'
            "```"
        ),
        ignore_extra=False,
    )
    @commands.guild_only()
    async def aircraft(self, ctx: commands.Context, query: str = commands.parameter(description=HELP_AC_ARG0)):
        ac = Aircraft.search(query)
        if ac.ac.valid:
            a = ac.ac
            apr = ac.parse_result
            modifiers = "".join(
                name
                for name, set_ in zip(
                    ["+SPD", "-FUEL", "-CO2", "+4X"], [apr.speed_mod, apr.fuel_mod, apr.co2_mod, apr.fourx_mod]
                )
                if set_
            )
            personnel = ", ".join(
                f"{c} {name}{'s' if c > 1 else ''}"
                for c, name in zip(
                    [a.pilots, a.crew, a.engineers, a.technicians], ["pilot", "crew", "engineer", "technician"]
                )
            )
            e = discord.Embed(
                title=f"{a.manufacturer} {a.name} (`{a.shortname}`, {a.type.name.split('.')[-1]})",
                description=(
                    f"**   Engine**: {a.ename}{modifiers} (id: {a.eid})\n"
                    f"**    Speed**: {a.speed:,.3f} km/h (rank: {a.priority+1})\n"
                    f"**     Fuel**: {a.fuel:.3f} lbs/km\n"
                    f"**     CO2**: {a.co2:.3f} kg/pax/km\n"
                    f"**     Cost**: ${a.cost:,}\n"
                    f"**   Capacity**: {a.capacity:,} {'lbs' if a.type == Aircraft.Type.CARGO else 'pax'}\n"
                    f"**   Runway**: {a.rwy:,} m\n"
                    f"**  Check cost**: ${a.check_cost:,}\n"
                    f"**   Range**: {a.range:,} km\n"
                    f"**Maintenance**: {a.maint:,} hr\n"
                    f"**    Ceiling**: {a.ceil:,} ft\n"
                    f"**  Personnel**: {personnel}\n"
                    f"** Dimensions**: length {a.length} × span {a.wingspan} m\n"
                ),
                color=COLOUR_GENERIC,
            )
            e.set_image(url=f"https://airlinemanager.com/{a.img}")
            await ctx.send(embed=e)
            return
        suggs = Aircraft.suggest(ac.parse_result)
        emb = sugg_embed(ac, suggs)
        if suggs:
            emb.add_field(
                name="Suggested commands:",
                value=(
                    "```sh\n"
                    f"{cfg.bot.COMMAND_PREFIX}help aircraft\n"
                    f"{cfg.bot.COMMAND_PREFIX}aircraft {suggs[0].ac.shortname}\n"
                    "```"
                ),
            )
        await ctx.send(embed=emb)
        return

    @aircraft.error
    async def aircraft_error(self, ctx: commands.Context, error: commands.CommandError):
        await handle_too_many_args(ctx, error, "query", "aircraft")


def sugg_embed(ac: Aircraft.SearchResult, suggs: list[Aircraft.Suggestion]) -> discord.Embed:
    extra = f" using search mode `{st}`" if (st := ac.parse_result.search_type) != Aircraft.SearchType.ALL else ""
    embed = discord.Embed(
        title=f"Aircraft `{ac.parse_result.search_str}` not found{extra}!",
        description="You may also want to check the validity of the engine option(s).",
        color=COLOUR_ERROR,
    )
    if suggs:
        embed.add_field(
            name="Did you mean:",
            value="\n".join(f"- `{a.ac.shortname}` ({a.ac.name})" for a in suggs),
            inline=False,
        )
    return embed
