import discord
from am4.utils.game import User
from discord import AllowedMentions
from discord.ext import commands

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


async def handle_too_many_args(ctx: commands.Context, error: commands.CommandError, arg_name: str, cmd: str):
    if isinstance(error, commands.TooManyArguments):
        pre = ctx.view.buffer[: ctx.view.previous]
        rest = ctx.view.buffer[ctx.view.index :]
        await ctx.send(
            embed=get_err_embed(
                title="Too many arguments!",
                desc=(
                    f"I interpreted the {arg_name} to be `{ctx.current_argument}` and "
                    f'saw the rest (`{rest}`) as invalid.\nTry wrapping your {arg_name} in double quotes (`"`).'
                ),
                suggested_commands=[
                    f"{cfg.bot.COMMAND_PREFIX}help {cmd}",
                    f'{pre}"{ctx.current_argument}{rest}"',
                ],
            )
        )
        return


async def handle_missing_arg(ctx: commands.Context, error: commands.CommandError, cmd: str):
    if isinstance(error, commands.MissingRequiredArgument):
        pre = ctx.view.buffer[: ctx.view.previous]
        cp = ctx.current_parameter
        await ctx.send(
            embed=get_err_embed(
                title="Missing required argument!",
                desc=(f"I expected the `{cp.name}` argument.\n"),
                suggested_commands=[f"{cfg.bot.COMMAND_PREFIX}help {cmd}", f"{pre} <{cp.name}>"],
            )
        )
        return


async def handle_bad_literal(ctx: commands.Context, error: commands.CommandError, cmd: str):
    if isinstance(error, commands.BadLiteralArgument):
        pre = ctx.view.buffer[: ctx.view.previous]
        cp = ctx.current_parameter
        valid_literals = ", ".join(f"`{l}`" for l in error.literals)
        await ctx.send(
            embed=get_err_embed(
                title="Provided argument is invalid!",
                desc=(f"I expected the `{cp.name}` to be one of: {valid_literals}\n"),
                suggested_commands=[f"{cfg.bot.COMMAND_PREFIX}help {cmd}", f"{pre}<{cp.name}>"],
            )
        )
        return
