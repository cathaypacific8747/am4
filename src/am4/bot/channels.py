from discord import TextChannel
from discord.ext import commands

from ..config import cfg


class _Channels:
    debug: TextChannel = None
    price_alert: TextChannel = None

    async def init(self, bot: commands.Bot):
        self.debug = await bot.fetch_channel(cfg.bot.DEBUG_CHANNELID)
        self.price_alert = await bot.fetch_channel(cfg.bot.PRICEALERT_CHANNELID)
        from loguru import logger

        logger.success("Channels initialised")


channels = _Channels()
