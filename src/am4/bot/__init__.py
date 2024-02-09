import asyncio

import discord
from am4.utils import __version__ as am4utils_version
from am4.utils.db import init as utils_init
from discord.ext.commands import Bot
from loguru import logger

from ..config import cfg
from .aircraft import AircraftCog
from .airport import AirportCog
from .help import HelpCog

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix=cfg.bot.COMMAND_PREFIX, intents=intents, help_command=None)


@bot.event
async def on_ready():
    logger.info(f'logged in as {bot.user} on {", ".join([g.name for g in bot.guilds])}')
    logger.info(f"am4.utils version {am4utils_version}")


async def start(db_done: asyncio.Event):
    await db_done.wait()
    utils_init()
    await bot.add_cog(HelpCog(bot))
    await bot.add_cog(AirportCog(bot))
    await bot.add_cog(AircraftCog(bot))
    await bot.start(cfg.bot.DISCORD_TOKEN)
