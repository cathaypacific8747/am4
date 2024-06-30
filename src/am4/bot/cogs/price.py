import time
from typing import Literal

import discord
from discord.ext import commands

from ...config import cfg
from ..base import BaseCog
from ..channels import channels
from ..converters import PriceCvtr
from ..errors import CustomErrHandler
from ..utils import COLOUR_ERROR, COLOUR_SUCCESS, main_server_only

HELP_FUEL = "Fuel or CO₂ price. Example: `f690` or `c130`."
ParsedPrice = tuple[Literal["Fuel", "CO₂"], float]


class PriceCog(BaseCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @commands.command(
        brief=f"Reports a price to <#{cfg.bot.PRICEALERT_CHANNELID}>",
        help=(
            "Pings everyone about a low price, examples:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}price f420\n"
            "```means: **F**uel is $ 420.```php\n"
            f"{cfg.bot.COMMAND_PREFIX}price c130\n"
            "```means: **C**O2 is $ 130.\nYou can also report both at the same time:```php\n"
            f"{cfg.bot.COMMAND_PREFIX}price f690 c130\n"
            "```means: Fuel is $ 690 and CO₂ is $ 130. Order does not matter.\n"
            "**:warning: Do not report fuel prices above $900 and CO₂ prices above $140.**"
        ),
        ignore_extra=False,
    )
    @main_server_only()
    async def price(
        self,
        ctx: commands.Context,
        price_0: ParsedPrice = commands.parameter(description=HELP_FUEL, converter=PriceCvtr),
        price_1: ParsedPrice | None = commands.parameter(description=HELP_FUEL, converter=PriceCvtr, default=None),
    ):
        for r in ctx.author.roles:
            if r.id == cfg.bot.PRICEALERTBAN_ROLEID:
                await ctx.send(
                    embed=discord.Embed(
                        title="You are not allowed to send price alerts.",
                        description="If you think this is a mistake, contact a moderator.",
                        colour=COLOUR_ERROR,
                    )
                )
                return
        t_now = time.time()
        t_start = t_now - t_now % 1800
        t_expiry_f = f"<t:{int(t_start+1800)}:R>"

        # format prices and construct embed
        prices = {p[0]: p[1] for p in [price_0, price_1] if p is not None}
        prices_f = ", ".join(f"{k} is ${v:.0f}" for k, v in sorted(prices.items(), key=lambda x: x[0], reverse=True))

        bounds = {
            "Fuel": (0.7, 300, 900),
            "CO₂": (0.3, 100, 140),
        }
        score = 0
        for k, v in prices.items():
            mul, vmin, vmax = bounds[k]
            s = 1 - (v - vmin) / (vmax - vmin)
            score += max(min(s, 1), 0) * mul

        async def send_update_success(jump_url: str, is_edit: bool = False):
            desc = f"{jump_url}\n> {prices_f}."
            if not is_edit:
                desc += (
                    f"\n\nIf there was a mistake, send the `{cfg.bot.COMMAND_PREFIX}price` command again "
                    f"**within 60 seconds** to update it. Otherwise, contact one of our <@&{cfg.bot.HELPER_ROLEID}>"
                    f"or <@&{cfg.bot.MODERATOR_ROLEID}>."
                )
            await ctx.send(
                embed=discord.Embed(
                    title=f"Price alert {'updated' if is_edit else 'sent'}!",
                    description=desc,
                    colour=COLOUR_SUCCESS,
                )
            )

        # if the the price is already sent, error if the user is not a mod, otherwise edit it
        async for msg in channels.price_alert.history(limit=1):
            if (t_now := msg.created_at.timestamp()) > t_start:
                for r in ctx.author.roles:
                    if r.id in [cfg.bot.MODERATOR_ROLEID, cfg.bot.HELPER_ROLEID] or t_now - t_start < 60:
                        old_senders = msg.content.split(". (Sent by ")[0].split(") ")[1]
                        await msg.edit(
                            content=(
                                f"{prices_f}. ({old_senders}, Updated by {ctx.author.mention}) "
                                f"<@&{cfg.bot.PRICEALERT_ROLEID}>"
                            )
                        )
                        await send_update_success(msg.jump_url)
                        return
                embed = discord.Embed(
                    title="Price alert already sent!",
                    description=(
                        f"{msg.jump_url}: Try again {t_expiry_f}.\n"
                        "If the current price is wrong, contact a moderator and they'll fix it."
                    ),
                    colour=COLOUR_ERROR,
                )
                await ctx.send(embed=embed, delete_after=1800 - (t_now - t_start))
                return

        # send a text-only version for push notifications, then enhance it with rich embed
        msg = await channels.price_alert.send(
            content=f"{prices_f}. (Sent by {ctx.author.mention}) <@&{cfg.bot.PRICEALERT_ROLEID}>"
        )
        await send_update_success(msg.jump_url)

    @price.error
    async def price_error(self, ctx: commands.Context, error: commands.CommandError):
        h = CustomErrHandler(ctx, error, "price")

        await h.invalid_price()
        await h.too_many_args("price")
        await h.common_mistakes()
        await h.raise_for_unhandled()
