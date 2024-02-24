import heapq
import io
import traceback
from typing import Annotated, Callable

import discord
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.db.utils import jaro_winkler_distance
from discord.ext import commands
from discord.ext.commands.view import StringView
from pydantic_core import PydanticCustomError, ValidationError
from rich import inspect
from rich.console import Console

from ..config import cfg
from .channels import channels

COLOUR_ERROR = discord.Colour(0xCA7575)
Suggestions = list[tuple[Annotated[str, "displayed value in command sugg"], Annotated[str, "full description"]]]


class AircraftNotFoundError(commands.BadArgument):
    def __init__(self, acsr: Aircraft.SearchResult):
        super().__init__("Aircraft not found!")
        self.acsr = acsr


class AirportNotFoundError(commands.BadArgument):
    def __init__(self, apsr: Airport.SearchResult):
        super().__init__("Airport not found!")
        self.apsr = apsr


class ValidationErrorBase(commands.BadArgument):
    def __init__(self, err: ValidationError | PydanticCustomError):
        super().__init__()
        self.err = err
        if isinstance(err, ValidationError):
            self.msg = "\n".join(f'`{",".join(e["loc"])}`: {e["msg"]}' for e in err.errors())
        elif isinstance(err, PydanticCustomError):
            self.msg = err.message()
        else:
            self.msg = ""


class SettingValueValidationError(ValidationErrorBase):
    pass


class TPDValidationError(ValidationErrorBase):
    pass


class CfgAlgValidationError(ValidationErrorBase):
    pass


class ConstraintValidationError(ValidationErrorBase):
    pass


class PriceValidationError(ValidationErrorBase):
    pass


def get_err_tb(v: StringView) -> str:
    highlight = " ▔▔▔?" if (wordlen := v.index - v.previous) < 1 else ("▔" * wordlen + "↖")
    return f"```php\n{v.buffer}\n{' ' * v.previous}{highlight}\n```"


class CustomErrHandler:
    def __init__(
        self, ctx: commands.Context, error: commands.CommandError = commands.CommandError(), cmd: str | None = None
    ):
        self.ctx = ctx
        self.error = error
        self.cmd = cmd

        self.err_tb = get_err_tb(self.ctx.view)

        self.handled = False

    async def raise_for_unhandled(self):
        if not self.handled:
            await self.ctx.send(
                embed=discord.Embed(
                    title="An error occurred!",
                    description=(
                        "Oops! Something real bad happened and I don't know how to handle it.\n"
                        "This incident has been reported to our developers."
                    ),
                    colour=COLOUR_ERROR,
                )
            )
            buf = io.StringIO()
            console = Console(file=buf)
            console.print_exception(show_locals=True)
            inspect(self.ctx, console=console)
            buf.seek(0)
            await channels.debug.send(
                f"`{self.ctx.message.content}` by {self.ctx.author.mention}: {self.ctx.message.jump_url}",
                file=discord.File(buf, filename="error.log"),
            )
            raise self.error

    def _get_err_embed(
        self, title: str, description: str | None, suggs: Suggestions | None = None, sugg_cmd_override: list[str] = []
    ) -> discord.Embed:
        emb = discord.Embed(title=title, description=description, colour=COLOUR_ERROR)
        if suggs is not None:
            if len(suggs) > 1:
                emb.add_field(name="Did you mean:", value="\n".join(f"- {desc}" for _k, desc in suggs), inline=False)
            if not sugg_cmd_override:
                v = self.ctx.view
                emb.add_field(
                    name="Suggested commands:",
                    value=(
                        "```php\n"
                        f"{cfg.bot.COMMAND_PREFIX}help {self.cmd}\n"
                        f"{v.buffer[:v.previous]}{suggs[0][0]}{v.buffer[v.index:]}\n"
                        "```"
                    ),
                    inline=False,
                )
        if sugg_cmd_override:
            emb.add_field(
                name="Suggested Commands:",
                value="```php\n" + "\n".join(sugg_cmd_override) + "```",
            )
        return emb

    async def invalid_aircraft(self):
        if not isinstance(self.error, AircraftNotFoundError):
            return
        acsr = self.error.acsr
        suggs = Aircraft.suggest(acsr.parse_result)

        extra = f" using search mode `{st}`" if (st := acsr.parse_result.search_type) != Aircraft.SearchType.ALL else ""
        extra_mod = "You might also want to check the engine modifiers." if "[" in self.ctx.current_argument else ""
        embed = self._get_err_embed(
            title=f"Aircraft `{self.ctx.current_argument}` not found{extra}!",
            description=f"{self.err_tb}{extra_mod}",
            suggs=[(a.ac.shortname, f"`{a.ac.shortname}` ({a.ac.name})") for a in suggs],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_airport(self):
        if not isinstance(self.error, AirportNotFoundError):
            return
        apsr = self.error.apsr
        suggs = Airport.suggest(apsr.parse_result)

        extra = f" using search mode `{st}`" if (st := apsr.parse_result.search_type) != Airport.SearchType.ALL else ""
        embed = self._get_err_embed(
            title=f"Airport `{self.ctx.current_argument}` not found{extra}!",
            description=self.err_tb,
            suggs=[(a.ap.iata.lower(), f"`{a.ap.iata}` / `{a.ap.icao}` ({a.ap.name}, {a.ap.country})") for a in suggs],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_setting_value(self):
        if not isinstance(self.error, SettingValueValidationError):
            return
        embed = self._get_err_embed(
            title="Invalid setting value!",
            description=f"{self.err_tb}Details:\n{self.error.msg}".strip(),
            suggs=[("<value>", "")],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_tpd(self):
        if not isinstance(self.error, TPDValidationError):
            return
        embed = self._get_err_embed(
            title="Invalid trips per day!",
            description=f"{self.err_tb}Details:\n{self.error.msg}".strip(),
            suggs=[("3", "")],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_cfg_alg(self):
        if not isinstance(self.error, CfgAlgValidationError):
            return
        embed = self._get_err_embed(
            title="Invalid configuration algorithm!",
            description=f"{self.err_tb}\n{self.error.msg}".strip(),
            suggs=[("AUTO", "")],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_constraint(self):
        if not isinstance(self.error, ConstraintValidationError):
            return
        as_time = self.error.err.errors()[0]["type"] == "time_delta_parsing"
        extra = (
            "**Tip**: I'm assuming the constraint is by time: correct it using `HH:MM`."
            if as_time
            else "**Tip**: I'm assuming the constraint is by distance: if you'd like to use time instead, use `HH:MM`."
        )
        suggs = [("08:00", "")] if as_time else [("08:00", ""), ("15000", "")]
        embed = self._get_err_embed(
            title="Invalid constraint!",
            description=f"{self.err_tb}\n{self.error.msg}\n{extra}".strip(),
            suggs=suggs,
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_price(self):
        if not isinstance(self.error, PriceValidationError):
            return
        embed = self._get_err_embed(
            title="Invalid price!",
            description=f"{self.err_tb}\n{self.error.msg}".strip(),
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def too_many_args(self, arg_name: str):
        if not isinstance(self.error, commands.TooManyArguments):
            return
        v = self.ctx.view
        # override
        highlight = "▔" * len(v.buffer[v.index + 1 :])
        err_loc = f"```php\n{v.buffer}\n{' ' * (v.index+1)}{highlight}\n```"

        cmds = [f"{cfg.bot.COMMAND_PREFIX}help {self.cmd}", f"{v.buffer[: v.index]}"]
        if a := self.ctx.current_argument:
            cmds.append(f'{v.buffer[: v.previous]}"{a}{v.buffer[v.index:]}"')

        await self.ctx.send(
            embed=self._get_err_embed(
                title="Too many arguments!",
                description=(
                    f"{err_loc}Tip: If you are trying to use spaces in the {arg_name},"
                    f' wrap it in double quotes (`"`).'
                ),
                sugg_cmd_override=cmds,
            )
        )
        self.handled = True

    async def missing_arg(self):
        if not isinstance(self.error, commands.MissingRequiredArgument):
            return
        pre = self.ctx.view.buffer[: self.ctx.view.previous]
        cp = self.ctx.current_parameter
        await self.ctx.send(
            embed=self._get_err_embed(
                title="Missing required argument!",
                description=(f"{self.err_tb}I expected the `{cp.name}` argument.\n"),
                sugg_cmd_override=[f"{cfg.bot.COMMAND_PREFIX}help {self.cmd}", f"{pre} <{cp.name}>"],
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
        embed = self._get_err_embed(
            title=f"Provided argument `{self.ctx.current_argument}` is invalid.",
            description=f"{self.err_tb}Here, the `{cp.name}` must be one of: {valid_literals}.",
            suggs=[(s, s) for s in suggs],
            sugg_cmd_override=get_cmd_suggs(suggs),
        )
        await self.ctx.send(embed=embed)
        self.handled = True
