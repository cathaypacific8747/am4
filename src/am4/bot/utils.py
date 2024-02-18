from typing import Literal

import discord
from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.demand import CargoDemand, PaxDemand
from am4.utils.game import User
from am4.utils.ticket import CargoTicket, PaxTicket, VIPTicket
from discord import AllowedMentions
from discord.ext import commands

from ..common import (
    HELP_U_FOURX,
    HELP_U_INCOME_LOSS_TOL,
    HELP_U_LOAD,
)
from ..config import cfg
from ..db.client import pb
from ..db.user import UserExtra
from .errors import CustomErrHandler

GUIDE_DEV_ROLEID = 646148607636144131
STAR_ROLEID = 701410528853098497

COLOUR_GENERIC = discord.Colour(0x9FACBD)
COLOUR_ERROR = discord.Colour(0xCA7575)
COLOUR_SUCCESS = discord.Colour(0x75CA83)
COLOUR_REALISM = discord.Colour(0x277ECD)
COLOUR_EASY = discord.Colour(0x1A7939)

IY = "<:economy:701335275896307742>"
IJ = "<:business:701335275669946431>"
IF = "<:first:701335275938381824>"
IL = "<:large:701335275690786817>"
IH = "<:heavy:701335275799969833>"

HELP_TPD = (
    "**How many departures per day, per aircraft**\n"
    "Multiple aircraft can be assigned the same route to minimise waste in demand.\n"
    "To force 1 aircraft per route, add `!` at the end. "
    "For example, `3!` assumes you depart one aircraft three times in a day.\n"
    "If not provided (default `AUTO`), the bot will attempt to maximise it."
)
HELP_CFG_ALG = (
    "**Configuration Algorithm**\n"
    f"- {','.join(f'`{c}`' for c in Aircraft.PaxConfig.Algorithm.__members__)} (pax)\n"
    f"- {','.join(f'`{c}`' for c in Aircraft.CargoConfig.Algorithm.__members__)} (cargo)\n"
    "The best algorithm is picked automatically depending on the route distance.\n"
    "`YJF` here denotes the order of priority when filling seats."
)
HELP_SETTING_KEY = (
    "**The setting key** - some important ones are:\n"
    f"- `fourx`: {HELP_U_FOURX}\n"
    f"- `income_loss_tol`: {HELP_U_INCOME_LOSS_TOL}\n"
    f"- `load`: {HELP_U_LOAD}\n"
)

_SP100 = " "
_SP050 = " "
_SP033 = " "
_SP025 = " "
_SP022 = " "
_SP016 = " "
_SPHAIR = " "
_SPPUNC = " "


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
        h = CustomErrHandler(ctx)
        embed = h._get_err_embed(
            title="Mismatched game mode!",
            description=(
                f"I detected the <@&{role_id}> role on your account, but your settings indicate "
                f"that you are in the `{gm_user}` game mode.\n"
            ),
            sugg_cmd_override=[f"{cfg.bot.COMMAND_PREFIX}settings set game_mode {gm_target}"],
        )
        await ctx.send(embed=embed, allowed_mentions=AllowedMentions.none())
    return user, user_extra


def format_ap_short(ap: Airport, mode: Literal[0, 1, 2]) -> str:
    indicator = "┏" if mode == 0 else "┣" if mode == 1 else "┗"
    return f"`{indicator} {ap.iata}` {ap.name}, {ap.country}"


def format_demand(pax_demand: PaxDemand, as_cargo: bool = False) -> str:
    if as_cargo:
        cargo_demand = CargoDemand(pax_demand)
        return f"{IL}`{cargo_demand.l:<7}` {IH}`{cargo_demand.h:<7}`"
    return f"{IY}`{pax_demand.y:<4}` {IJ}`{pax_demand.j:<5}` {IF}`{pax_demand.f:<5}`"


def format_config(cfg: Aircraft.PaxConfig | Aircraft.CargoConfig) -> str:
    if isinstance(cfg, Aircraft.CargoConfig):
        return f"{IL}`{cfg.l:<7}` {IH}`{cfg.h:<7}`"
    return f"{IY}`{cfg.y:<4}` {IJ}`{cfg.j:<5}` {IF}`{cfg.f:<5}`"


def format_ticket(ticket: PaxTicket | CargoTicket | VIPTicket) -> str:
    if isinstance(ticket, CargoTicket):
        return f"{IL}`{ticket.l:<7}` {IH}`{ticket.h:<7}`"
    return f"{IY}`{ticket.y:<4}` {IJ}`{ticket.j:<5}` {IF}`{ticket.f:<5}`"


def format_modifiers(apr: Aircraft):
    return "".join(
        name
        for name, set_ in zip(
            ["+SPD", "-FUEL", "-CO2", "+4X"], [apr.speed_mod, apr.fuel_mod, apr.co2_mod, apr.fourx_mod]
        )
        if set_
    )
