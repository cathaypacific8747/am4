import heapq
from typing import Literal

import discord
from am4.utils.db.utils import jaro_winkler_distance
from am4.utils.game import User
from discord.ext import commands
from pydantic import ValidationError

from ...config import cfg
from ...db.models.game import PyUser, pyuser_whitelisted_keys
from ..utils import (
    COLOUR_GENERIC,
    fetch_user_info,
    get_err_embed,
    handle_bad_literal,
    handle_missing_arg,
    handle_too_many_args,
)


def suggest_setting_keys(k_input: str) -> list[str]:
    top_keys = []
    for k in pyuser_whitelisted_keys:
        heapq.heappush(top_keys, (jaro_winkler_distance(k_input, k), k))
    return [k for _, k in heapq.nlargest(3, top_keys)]


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
        brief="show all of my settings",
        help=("Show all settings, example:```php\n" f"{cfg.bot.COMMAND_PREFIX}settings show\n" "```"),
        ignore_extra=False,
    )
    async def show(self, ctx: commands.Context):
        u, _ue = await fetch_user_info(ctx)
        e = discord.Embed(
            title=f"Settings for `@{u.username}`)",
            description=(
                f"`        game_mode`: {'Easy' if u.game_mode == User.GameMode.EASY else 'Realism'}\n"
                f"`          game_id`: {u.game_id}\n"
                f"`        game_name`: {u.game_name}\n"
                f"`             load`: {u.load:.2%}\n"
                f"`  income_loss_tol`: {u.income_loss_tol:.2%}\n"
                f"`    wear_training`: {u.wear_training}\n"
                f"`  repair_training`: {u.repair_training}\n"
                f"`       h_training`: {u.h_training}\n"
                f"`       l_training`: {u.l_training}\n"
                f"`     co2_training`: {u.co2_training}\n"
                f"`    fuel_training`: {u.fuel_training}\n"
                f"`        co2_price`: {u.co2_price}\n"
                f"`       fuel_price`: {u.fuel_price}\n"
                f"`            fourx`: {'Yes' if u.fourx else 'No'}\n"
                f"`accumulated_count`: {u.accumulated_count}\n"
            ),
            color=COLOUR_GENERIC,
        )
        e.add_field(
            name="To modify a setting, use",
            value=f"```php\n{cfg.bot.COMMAND_PREFIX}settings set <setting key> <value>\n```",
        )
        await ctx.send(embed=e)

    @settings.command(
        brief="set one of my settings",
        help=(
            "Set a specific setting given a *setting key* and a *value*, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}settings set xxx yyy\n"
            "```"
        ),
        ignore_extra=False,
    )
    async def set(self, ctx: commands.Context, key: str, value: str | int | float | bool):
        # check whether key is whitelisted, and value conforms to pydantic, if so, update db.
        if key not in pyuser_whitelisted_keys:
            sugg_keys = suggest_setting_keys(key)
            await ctx.send(
                embed=get_err_embed(
                    title=f"Setting key `{key}` is invalid.",
                    desc=(
                        "The provided setting key is not valid. Did you mean:\n"
                        + "\n".join(f"- `{k}`" for k in sugg_keys)
                    ),
                    suggested_commands=[
                        f"{cfg.bot.COMMAND_PREFIX}help settings set",
                        f"{cfg.bot.COMMAND_PREFIX}settings set {sugg_keys[0]} <value>",
                    ],
                )
            )
            return

        try:
            u_new = PyUser.__pydantic_validator__.validate_assignment(PyUser.model_construct(), key, value)
        except ValidationError as err:
            await ctx.send(
                embed=get_err_embed(
                    title=f"Invalid setting value `{value}` for key `{key}`",
                    desc="\n".join(f"- {','.join(f'`{l}`' for l in e['loc'])}: {e['msg']}" for e in err.errors()),
                    suggested_commands=[
                        f"{cfg.bot.COMMAND_PREFIX}help settings set",
                        f"{cfg.bot.COMMAND_PREFIX}settings set {key} <value>",
                    ],
                )
            )
            return

        v_new = getattr(u_new, key)
        u, _ue = await fetch_user_info(ctx)
        print(u.id)
        await ctx.send(f"{v_new=}")

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
