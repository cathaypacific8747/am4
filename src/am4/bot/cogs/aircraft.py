import discord
from am4.utils.aircraft import Aircraft
from discord.ext import commands

from ...common import HELP_AC_ARG0
from ...config import cfg
from ..utils import COLOUR_GENERIC, CustomErrHandler, get_aircraft


class AircraftCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Finds an aircraft",
        help=(
            "Finds information about an aircraft given a *query*, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}aircraft a388\n"
            f"{cfg.bot.COMMAND_PREFIX}aircraft b744[2]\n"
            f'{cfg.bot.COMMAND_PREFIX}aircraft "ATR 42-300[sfcx]"\n'
            "```"
        ),
        ignore_extra=False,
    )
    @commands.guild_only()
    async def aircraft(self, ctx: commands.Context, query: str = commands.parameter(description=HELP_AC_ARG0)):
        ac = get_aircraft(query)
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
                f"**    Speed**: {a.speed:,.2f} km/h (rank: {a.priority+1})\n"
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

    @aircraft.error
    async def aircraft_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error)

        def get_cmd_suggs(suggs: list[Aircraft.Suggestion]):
            return [
                f"{cfg.bot.COMMAND_PREFIX}help aircraft",
                f"{cfg.bot.COMMAND_PREFIX}aircraft {suggs[0].ac.shortname}",
            ]

        await h.invalid_aircraft(get_cmd_suggs)
        await h.missing_arg("aircraft")
        await h.too_many_args("query", "aircraft")
        h.raise_for_unhandled()
