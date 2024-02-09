import discord
from discord.ext import commands

from ..config import cfg

GUIDE_DEV_ROLEID = 646148607636144131
STAR_ROLEID = 701410528853098497

COLOUR_GENERIC = discord.Colour(0x9FACBD)
COLOUR_ERROR = discord.Colour(0xCA7575)

_SP100 = " "
_SP050 = " "
_SP033 = " "
_SP025 = " "
_SP022 = " "
_SP016 = " "
_SPHAIR = " "
_SPPUNC = " "


async def handle_too_many_args(ctx: commands.Context, error: commands.CommandError, arg_name: str, cmd: str):
    if isinstance(error, commands.TooManyArguments):
        rest = ctx.view.buffer[ctx.view.index :]
        emb = discord.Embed(
            title="Too many arguments!",
            description=(
                f"I interpreted the {arg_name} to be `{ctx.current_argument}` and "
                f'saw the rest (`{rest}`) as invalid.\nTry wrapping your query in double quotes (`"`).'
            ),
            color=COLOUR_ERROR,
        )
        emb.add_field(
            name="Suggested Commands:",
            value=(
                "```sh\n"
                f"{cfg.bot.COMMAND_PREFIX}help {cmd}\n"
                f"{cfg.bot.COMMAND_PREFIX}{cmd} {ctx.current_argument}{rest}\n"
                "```"
            ),
        )
        await ctx.send(embed=emb)
        return
    raise error
