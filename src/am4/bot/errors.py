import heapq
from typing import Callable

import discord
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.db.utils import jaro_winkler_distance
from discord.ext import commands
from discord.ext.commands.view import StringView

from ..config import cfg

COLOUR_ERROR = discord.Colour(0xCA7575)


def get_err_embed(
    title: str | None = None, desc: str | None = None, suggested_commands: list[str] = []
) -> discord.Embed:
    emb = discord.Embed(title=title, description=desc, color=COLOUR_ERROR)
    if suggested_commands:
        emb.add_field(
            name="Suggested Commands:",
            value="```php\n" + "\n".join(suggested_commands) + "```",
        )
    return emb


class AircraftNotFoundError(commands.BadArgument):
    def __init__(self, acsr: Aircraft.SearchResult):
        super().__init__("Aircraft not found!")
        self.acsr = acsr


class AirportNotFoundError(commands.BadArgument):
    def __init__(self, apsr: Airport.SearchResult):
        super().__init__("Airport not found!")
        self.apsr = apsr


def get_err_tb(v: StringView) -> str:
    highlight = " ▔▔▔?" if (wordlen := v.index - v.previous) < 1 else ("▔" * wordlen + "↖")
    return f"```php\n{v.buffer}\n{' ' * v.previous}{highlight}\n```"


class CustomErrHandler:
    def __init__(self, ctx: commands.Context, error: commands.CommandError):
        self.ctx = ctx
        self.error = error

        self.err_tb = get_err_tb(self.ctx.view)

        self.handled = False

    def raise_for_unhandled(self):
        if not self.handled:
            raise self.error

    async def invalid_aircraft(self, cmd: str):
        if not isinstance(self.error, AircraftNotFoundError):
            return
        acsr = self.error.acsr
        suggs = Aircraft.suggest(acsr.parse_result)

        extra = f" using search mode `{st}`" if (st := acsr.parse_result.search_type) != Aircraft.SearchType.ALL else ""
        embed = discord.Embed(
            title=f"Aircraft `{self.ctx.current_argument}` not found{extra}!",
            description=self.err_tb
            + ("You might also want to check the engine modifiers." if "[" in self.ctx.current_argument else ""),
            color=COLOUR_ERROR,
        )
        v = self.ctx.view
        if suggs:
            embed.add_field(
                name="Did you mean:",
                value="\n".join(f"- `{a.ac.shortname}` ({a.ac.name})" for a in suggs),
                inline=False,
            )
            embed.add_field(
                name="Suggested commands:",
                value=(
                    "```php\n"
                    f"{cfg.bot.COMMAND_PREFIX}help {cmd}\n"
                    f"{v.buffer[:v.previous]}{suggs[0].ac.shortname}{v.buffer[v.index:]}\n"
                    "```"
                ),
                inline=False,
            )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_airport(self, cmd: str):
        if not isinstance(self.error, AirportNotFoundError):
            return
        apsr = self.error.apsr
        suggs = Airport.suggest(apsr.parse_result)

        extra = f" using search mode `{st}`" if (st := apsr.parse_result.search_type) != Airport.SearchType.ALL else ""
        embed = discord.Embed(
            title=f"Airport `{self.ctx.current_argument}` not found{extra}!",
            description=self.err_tb,
            color=COLOUR_ERROR,
        )
        v = self.ctx.view
        if suggs:
            embed.add_field(
                name="Did you mean:",
                value="\n".join(f"- `{a.ap.iata}` / `{a.ap.icao}` ({a.ap.name}, {a.ap.country})" for a in suggs),
                inline=False,
            )
            embed.add_field(
                name="Suggested commands:",
                value=(
                    "```php\n"
                    f"{cfg.bot.COMMAND_PREFIX}help {cmd}\n"
                    f"{v.buffer[:v.previous]}{suggs[0].ap.iata.lower()}{v.buffer[v.index:]}\n"
                    "```"
                ),
                inline=False,
            )

        await self.ctx.send(embed=embed)
        self.handled = True

    async def too_many_args(self, arg_name: str, cmd: str):
        if not isinstance(self.error, commands.TooManyArguments):
            return
        v = self.ctx.view
        # override
        highlight = "▔" * len(v.buffer[v.index + 1 :])
        err_loc = f"```php\n{v.buffer}\n{' ' * (v.index+1)}{highlight}\n```"

        cmds = [f"{cfg.bot.COMMAND_PREFIX}help {cmd}", f"{v.buffer[: v.index]}"]
        if a := self.ctx.current_argument:
            cmds.append(f'{v.buffer[: v.previous]}"{a}{v.buffer[v.index:]}"')

        await self.ctx.send(
            embed=get_err_embed(
                title="Too many arguments!",
                desc=(
                    f"{err_loc}Tip: If you are trying to use spaces in the {arg_name},"
                    f' wrap it in double quotes (`"`).'
                ),
                suggested_commands=cmds,
            )
        )
        self.handled = True

    async def missing_arg(self, cmd: str):
        if not isinstance(self.error, commands.MissingRequiredArgument):
            return
        pre = self.ctx.view.buffer[: self.ctx.view.previous]
        cp = self.ctx.current_parameter
        await self.ctx.send(
            embed=get_err_embed(
                title="Missing required argument!",
                desc=(f"{self.err_tb}I expected the `{cp.name}` argument.\n"),
                suggested_commands=[f"{cfg.bot.COMMAND_PREFIX}help {cmd}", f"{pre} <{cp.name}>"],
            )
        )
        self.handled = True

    async def bad_literal(self, get_cmd_suggs: Callable[[list[str]], list[str]]):
        if not isinstance(self.error, commands.BadLiteralArgument):
            return

        valid_literals = ", ".join(f"`{l}`" for l in self.error.literals)
        top_keys = []
        for k in self.error.literals:
            heapq.heappush(top_keys, (jaro_winkler_distance(self.error.argument, k), k))
        suggs = [k for _, k in heapq.nlargest(3, top_keys)]

        cp = self.ctx.current_parameter
        embed = discord.Embed(
            title=f"Provided argument `{self.ctx.current_argument}` is invalid.",
            description=f"{self.err_tb}Here, the `{cp.name}` must be one of: {valid_literals}.",
            color=COLOUR_ERROR,
        )
        cmds = "\n".join(get_cmd_suggs(suggs))
        if suggs:
            embed.add_field(
                name="Did you mean:",
                value="\n".join(f"- `{k}`" for k in suggs),
                inline=False,
            )
            embed.add_field(name="Suggested commands:", value=f"```php\n{cmds}\n```", inline=False)
        await self.ctx.send(embed=embed)
        self.handled = True
