import discord
from discord.ext import commands
import am4utils

from src.am4bot.config import Config

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=Config.COMMAND_PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} on {", ".join([g.name for g in bot.guilds])}')
    am4utils.db.init(am4utils.__path__[0])
    print(f'am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]} loaded')

@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send('pong')

@bot.command()
async def airport(ctx: commands.Context, a: str):
    try:
        a0 = am4utils.airport.from_auto(a)
        await ctx.send(a0.name)
    except am4utils.airport.AirportNotFoundException:
        await ctx.send('airport not found')