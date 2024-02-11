import discord
from am4.utils.game import User
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
    local_is_realism = discord.utils.get(u.roles, name="Realism") is not None
    user, user_extra, dbstatus = await pb.users.get_from_discord(
        u.name, u.nick, "REALISM" if local_is_realism else "EASY", u.id
    )
    if dbstatus == "created":
        await ctx.send(
            embed=discord.Embed(
                title="Your account has been created.",
                description=(
                    "You can modify your game mode, reputation and other settings "
                    f"with the `{cfg.bot.COMMAND_PREFIX}settings` command.\n"
                    "They will be automatically applied when using the bot's commands.\n\n"
                    f"To view your settings, use `{cfg.bot.COMMAND_PREFIX}settings show`.\n"
                    f"Learn more about the settings with `{cfg.bot.COMMAND_PREFIX}help settings`."
                ),
                color=COLOUR_SUCCESS,
            )
        )
    if local_is_realism and user.game_mode == User.GameMode.EASY:
        await ctx.send(
            embed=get_err_embed(
                title="You are in the wrong game mode!",
                desc=(
                    "I detected the `Realism` role on your account, but your settings indicate"
                    " that you are in the Easy game mode.\n"
                ),
                suggested_commands=[f"{cfg.bot.COMMAND_PREFIX}settings set game_mode realism"],
            )
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
