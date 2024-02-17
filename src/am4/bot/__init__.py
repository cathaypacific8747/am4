import asyncio

import discord
from am4.utils import __version__ as am4utils_version
from am4.utils.db import init as utils_init
from discord.ext.commands import Bot
from loguru import logger

from ..config import cfg
from .cogs.aircraft import AircraftCog
from .cogs.airport import AirportCog
from .cogs.help import HelpCog
from .cogs.route import RouteCog
from .cogs.routes import RoutesCog
from .cogs.settings import SettingsCog

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix=cfg.bot.COMMAND_PREFIX, intents=intents, help_command=None)


@bot.event
async def on_ready():
    logger.info(f'logged in as {bot.user} on {", ".join([g.name for g in bot.guilds])}')
    logger.info(f"am4.utils version {am4utils_version}")


@bot.event
async def on_error(event, *args, **kwargs):
    logger.exception(f"Error in {event} with args {args} and kwargs {kwargs}")


async def start(db_done: asyncio.Event):
    await db_done.wait()
    utils_init()
    await bot.add_cog(HelpCog(bot))
    await bot.add_cog(SettingsCog(bot))
    await bot.add_cog(AirportCog(bot))
    await bot.add_cog(AircraftCog(bot))
    await bot.add_cog(RouteCog(bot))
    await bot.add_cog(RoutesCog(bot))
    await bot.start(cfg.bot.DISCORD_TOKEN)
