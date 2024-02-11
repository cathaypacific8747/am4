from typing import Literal

import discord
from discord.ext import commands

from ...config import cfg
from ..utils import (
    get_user,
    handle_bad_literal,
    handle_missing_arg,
    handle_too_many_args,
)


class SettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(
        brief="Show, set or reset my settings",
        help=(
            "Shows setting(s), set a specific value given a *setting key*, or just reset it. For more information:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}help settings show\n"
            f"{cfg.bot.COMMAND_PREFIX}help settings set\n"
            f"{cfg.bot.COMMAND_PREFIX}help settings reset\n"
            "```"
        ),
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def settings(
        self,
        ctx: commands.Context,
        action: Literal["show", "set", "reset"] = commands.parameter(description="Action to perform"),
    ):
        pass

    @settings.command(
        brief="show all or one of my settings",
        help=(
            "Show all settings, or a specific setting given a *setting key*, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}settings show *\n"
            f"{cfg.bot.COMMAND_PREFIX}settings show userid\n"
            "```"
        ),
        ignore_extra=False,
    )
    async def show(self, ctx: commands.Context, key: str = commands.parameter(description="Setting key")):
        u, ue = await get_user(ctx.author)
        await ctx.send(str(u.to_dict()))
        if key == "*":
            await ctx.send("TODO: show all settings")
            return

        await ctx.send("TODO: show settings")

    @settings.command(
        brief="set one of my settings",
        help=(
            "Set a specific setting given a *setting key* and a *value*, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}settings set xxx yyy\n"
            "```"
        ),
        ignore_extra=False,
    )
    async def set(self, ctx: commands.Context, key: str, value: str):
        await ctx.send(f"TODO: Set setting {key} to {value}")

    @settings.command(
        brief="reset one of my settings",
        help=(
            "Reset a specific setting given a *setting key*, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}settings reset xxx\n"
            "```"
        ),
        ignore_extra=False,
    )
    async def reset(self, ctx: commands.Context, key: str):
        await ctx.send(f"TODO: Reset setting {key}")

    @settings.error
    async def settings_error(self, ctx: commands.Context, error: commands.CommandError):
        await handle_bad_literal(ctx, error, "settings")
        await handle_missing_arg(ctx, error, "settings")
        await handle_too_many_args(ctx, error, "action", "settings")
        raise error

    @show.error
    async def show_error(self, ctx: commands.Context, error: commands.CommandError):
        await handle_missing_arg(ctx, error, "settings show")
        await handle_too_many_args(ctx, error, "setting key", "settings show")
        raise error

    @set.error
    async def set_error(self, ctx: commands.Context, error: commands.CommandError):
        await handle_missing_arg(ctx, error, "settings reset")
        await handle_too_many_args(ctx, error, "setting key and value", "settings set")
        raise error

    @reset.error
    async def reset_error(self, ctx: commands.Context, error: commands.CommandError):
        await handle_missing_arg(ctx, error, "settings reset")
        await handle_too_many_args(ctx, error, "setting key", "settings reset")
        raise error
