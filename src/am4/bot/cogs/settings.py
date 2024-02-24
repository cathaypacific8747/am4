from typing import Literal

import discord
from am4.utils.game import User
from discord.ext import commands

from ...config import cfg
from ...db.client import pb
from ...db.models.game import PyUserWhitelistedKeys
from ..base import BaseCog
from ..converters import SettingValueCvtr
from ..errors import CustomErrHandler
from ..utils import COLOUR_GENERIC, COLOUR_SUCCESS, HELP_SETTING_KEY, fetch_user_info


class SettingsCog(BaseCog):
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
            name="Suggested commands:",
            value=(
                "```php\n"
                f"{cfg.bot.COMMAND_PREFIX}help settings\n"
                f"{cfg.bot.COMMAND_PREFIX}settings set game_mode realism\n"
                f"{cfg.bot.COMMAND_PREFIX}settings set load 87%\n"
                f"{cfg.bot.COMMAND_PREFIX}settings set training max\n```"
            ),
        )
        await ctx.send(embed=e)

    @settings.command(
        brief="set one of my settings",
        help=(
            "Set a specific setting given a *setting key* and a *value*, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}settings set game_mode realism\n"
            "```For convenience, you can set training to max by running:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}settings set training max\n"
            "```"
        ),
        ignore_extra=False,
    )
    async def set(
        self,
        ctx: commands.Context,
        key: Literal[PyUserWhitelistedKeys, "training"] = commands.parameter(description=HELP_SETTING_KEY),
        value: str = commands.parameter(converter=SettingValueCvtr, description="The setting value"),
    ):
        u, _ue = await fetch_user_info(ctx)
        dbstatus = await pb.users.update_setting(u.id, key, value)
        if dbstatus == "updated":
            if key == "training":
                description = f"All training values have been updated to {value:>1}.\n\n"
            else:
                v_old = u.to_dict().get(key, "---")
                description = f"The setting `{key}` has been updated from `{v_old:>1}` to `{value:>1}`.\n\n"

            await ctx.send(
                embed=discord.Embed(
                    title="Success",
                    description=f"{description}To view your settings, use `{cfg.bot.COMMAND_PREFIX}settings show`.\n",
                    color=COLOUR_SUCCESS,
                ),
            )

    @settings.command(
        brief="reset one of my settings",
        help=(
            "Reset a specific setting given a *setting key*, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}settings reset xxx\n"
            "```"
        ),
        ignore_extra=False,
    )
    async def reset(
        self,
        ctx: commands.Context,
        key: PyUserWhitelistedKeys = commands.parameter(description=HELP_SETTING_KEY),
    ):
        u, _ue = await fetch_user_info(ctx)
        v_old = getattr(u, key)
        u_new = User.Default(realism=u.game_mode == User.GameMode.REALISM)
        v_new = getattr(u_new, key)
        if key == "game_name":
            v_new = ctx.author.display_name
        dbstatus = await pb.users.update_setting(u.id, key, v_new)

        if dbstatus == "updated":
            await ctx.send(
                embed=discord.Embed(
                    title="Success",
                    description=(
                        f"The setting `{key}` has been reset from `{v_old:>1}` back to `{v_new:>1}`.\n\n"
                        f"To view your settings, use `{cfg.bot.COMMAND_PREFIX}settings show`.\n"
                    ),
                    color=COLOUR_SUCCESS,
                ),
            )

    @settings.error
    async def settings_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error, "settings")

        def get_cmd_suggs(suggs: list[str]):
            return [
                f"{cfg.bot.COMMAND_PREFIX}help settings",
                f"{cfg.bot.COMMAND_PREFIX}settings {suggs[0]}",
            ]

        await h.bad_literal(get_cmd_suggs)
        await h.missing_arg()
        await h.too_many_args("action")
        h.raise_for_unhandled()

    @show.error
    async def show_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error, "settings show")
        await h.too_many_args("action")
        h.raise_for_unhandled()

    @set.error
    async def set_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error, "settings set")

        def get_cmd_suggs(suggs: list[str]):
            return [
                f"{cfg.bot.COMMAND_PREFIX}help settings set",
                f"{cfg.bot.COMMAND_PREFIX}settings set {suggs[0]} <value>",
            ]

        await h.bad_literal(get_cmd_suggs)
        await h.invalid_setting_value()
        await h.missing_arg()
        await h.too_many_args("key/value")
        h.raise_for_unhandled()

    @reset.error
    async def reset_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error, "settings reset")

        def get_cmd_suggs(suggs: list[str]):
            return [
                f"{cfg.bot.COMMAND_PREFIX}help settings reset",
                f"{cfg.bot.COMMAND_PREFIX}settings reset {suggs[0]}",
            ]

        await h.bad_literal(get_cmd_suggs)
        await h.missing_arg()
        await h.too_many_args("key")
        h.raise_for_unhandled()
