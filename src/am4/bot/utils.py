import discord
from am4.utils.game import User
from discord import AllowedMentions
from discord.ext import commands

from ..config import cfg
from ..db.client import pb
from ..db.user import UserExtra
from .errors import CustomErrHandler

GUIDE_DEV_ROLEID = 646148607636144131
STAR_ROLEID = 701410528853098497

COLOUR_GENERIC = discord.Colour(0x9FACBD)
COLOUR_ERROR = discord.Colour(0xCA7575)
COLOUR_SUCCESS = discord.Colour(0x75CA83)

IY = "<:economy:701335275896307742>"
IJ = "<:business:701335275669946431>"
IF = "<:first:701335275938381824>"
IL = "<:large:701335275690786817>"
IH = "<:heavy:701335275799969833>"

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
