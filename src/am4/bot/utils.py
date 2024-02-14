import heapq
from typing import Callable

import discord
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.db.utils import jaro_winkler_distance
from am4.utils.game import User
from discord import AllowedMentions
from discord.ext import commands
from discord.ext.commands.view import StringView

from ..config import cfg
from ..db.client import pb
from ..db.user import UserExtra

GUIDE_DEV_ROLEID = 646148607636144131
STAR_ROLEID = 701410528853098497

COLOUR_GENERIC = discord.Colour(0x9FACBD)
COLOUR_ERROR = discord.Colour(0xCA7575)
COLOUR_SUCCESS = discord.Colour(0x75CA83)

_SP100 = " "
_SP050 = " "
_SP033 = " "
_SP025 = " "
_SP022 = " "
_SP016 = " "
_SPHAIR = " "
_SPPUNC = " "


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


async def fetch_user_info(ctx: commands.Context) -> tuple[User, UserExtra]:
    u = ctx.author
    r_role = discord.utils.get(u.roles, name="Realism")
    e_role = discord.utils.get(u.roles, name="Easy")
    gm_target = "Realism" if r_role is not None else "Easy"
    role_id = r_role.id if r_role is not None else e_role.id if e_role is not None else None

    user, user_extra, dbstatus = await pb.users.get_from_discord(u.name, u.nick, gm_target.upper(), u.id)
    if dbstatus == "created":
        gm_reason = f" because of your <@&{role_id}> role" if role_id is not None else ""
        await ctx.send(
            embed=discord.Embed(
                title="Your account has been created.",
                description=(
                    f"Your game mode is now `{gm_target}`{gm_reason}.\n\n"
                    f"To view your settings, use `{cfg.bot.COMMAND_PREFIX}settings show`.\n"
                    f"Need help with settings? Try `{cfg.bot.COMMAND_PREFIX}help settings`."
                ),
                color=COLOUR_SUCCESS,
            ),
            allowed_mentions=AllowedMentions.none(),
        )
    if (r_role is not None and user.game_mode == User.GameMode.EASY) or (
        e_role is not None and user.game_mode == User.GameMode.REALISM
    ):
        gm_user = "Realism" if user.game_mode == User.GameMode.REALISM else "Easy"
        await ctx.send(
            embed=get_err_embed(
                title="Mismatched game mode!",
                desc=(
                    f"I detected the <@&{role_id}> role on your account, but your settings indicate "
                    f"that you are in the `{gm_user}` game mode.\n"
                ),
                suggested_commands=[f"{cfg.bot.COMMAND_PREFIX}settings set game_mode {gm_target}"],
            ),
            allowed_mentions=AllowedMentions.none(),
        )
    return user, user_extra


class AircraftNotFoundError(commands.BadArgument):
    def __init__(self, acsr: Aircraft.SearchResult):
        super().__init__("Aircraft not found!")
        self.acsr = acsr


def get_aircraft(query: str) -> Aircraft.SearchResult:
    acsr = Aircraft.search(query)
    if not acsr.ac.valid:
        raise AircraftNotFoundError(acsr)
    return acsr


class AirportNotFoundError(commands.BadArgument):
    def __init__(self, apsr: Airport.SearchResult):
        super().__init__("Airport not found!")
        self.apsr = apsr


def get_airport(query: str) -> Airport.SearchResult:
    acsr = Airport.search(query)
    if not acsr.ap.valid:
        raise AirportNotFoundError(acsr)
    return acsr


def get_err_tb(v: StringView) -> str:
    highlight = " ▔▔▔?" if (wordlen := v.index - v.previous) < 1 else "▔" * wordlen
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

    async def invalid_aircraft(self, get_cmd_suggs: Callable[[list[Aircraft.Suggestion]], list[str]]):
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
        cmds = "\n".join(get_cmd_suggs(suggs))
        if suggs:
            embed.add_field(
                name="Did you mean:",
                value="\n".join(f"- `{a.ac.shortname}` ({a.ac.name})" for a in suggs),
                inline=False,
            )
            embed.add_field(name="Suggested commands:", value=f"```php\n{cmds}\n```", inline=False)
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_airport(self, get_cmd_suggs: Callable[[list[Airport.Suggestion]], list[str]]):
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
        cmds = "\n".join(get_cmd_suggs(suggs))
        if suggs:
            embed.add_field(
                name="Did you mean:",
                value="\n".join(f"- `{a.ap.iata}` / `{a.ap.icao}` ({a.ap.name}, {a.ap.country})" for a in suggs),
                inline=False,
            )
            embed.add_field(name="Suggested commands:", value=f"```php\n{cmds}\n```", inline=False)

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
