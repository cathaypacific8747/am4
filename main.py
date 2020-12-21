import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='CRITICAL', milliseconds=True) # info
logger.info("Started.")

import discord # pip install discord.py
from discord.ext import commands
TOKEN = "***REMOVED***"
logger.info("Loaded discord.py.")

# standard modules
import ctypes
import time

if True: # initialise and setup C functions
    f = ctypes.CDLL('./am4functions.so')

    if True: # initialise ticket prices functions.
        yTicket_easy = f.yTicket_easy
        yTicket_easy.argtypes = [ctypes.c_double]
        yTicket_easy.restype = ctypes.c_int

        jTicket_easy = f.yTicket_easy
        jTicket_easy.argtypes = [ctypes.c_double]
        jTicket_easy.restype = ctypes.c_int

        fTicket_easy = f.yTicket_easy
        fTicket_easy.argtypes = [ctypes.c_double]
        fTicket_easy.restype = ctypes.c_int

        yTicket_realism = f.yTicket_easy
        yTicket_realism.argtypes = [ctypes.c_double]
        yTicket_realism.restype = ctypes.c_int

        jTicket_realism = f.yTicket_easy
        jTicket_realism.argtypes = [ctypes.c_double]
        jTicket_realism.restype = ctypes.c_int

        fTicket_realism = f.yTicket_easy
        fTicket_realism.argtypes = [ctypes.c_double]
        fTicket_realism.restype = ctypes.c_int

        lTicket_easy = f.lTicket_easy
        lTicket_easy.argtypes = [ctypes.c_double]
        lTicket_easy.restype = ctypes.c_double

        hTicket_easy = f.lTicket_easy
        hTicket_easy.argtypes = [ctypes.c_double]
        hTicket_easy.restype = ctypes.c_double

        lTicket_realism = f.lTicket_easy
        lTicket_realism.argtypes = [ctypes.c_double]
        lTicket_realism.restype = ctypes.c_double

        hTicket_realism = f.lTicket_easy
        hTicket_realism.argtypes = [ctypes.c_double]
        hTicket_realism.restype = ctypes.c_double
        logger.info("Loaded all ticket functions.")

    f.initAirports.argtypes = None
    f.initAirports.restype = ctypes.c_bool
    if f.initAirports():
        logger.info("Loaded all airports in memory.")
    else:
        logger.critical("Loading airports failed.")

    routes = f.routes
    routes.argtypes = [ctypes.c_int]
    routes.restype = None

    class paxConf(ctypes.Structure):
        _fields_ = [("yConf", ctypes.c_int), ("jConf", ctypes.c_int), ("fConf", ctypes.c_int), ("maxIncome", ctypes.c_double), ("planesPerRoute", ctypes.c_int)]

    class cargoConf(ctypes.Structure):
        _fields_ = [("lPct", ctypes.c_double), ("hPct", ctypes.c_double), ("maxIncome", ctypes.c_double), ("planesPerRoute", ctypes.c_int)]

    brutePaxConf = f.brutePaxConf
    brutePaxConf.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool]
    brutePaxConf.restype = paxConf

    bruteCargoConf = f.bruteCargoConf
    bruteCargoConf.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool]
    bruteCargoConf.restype = cargoConf

    distance = f.distance
    distance.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    distance.restype = ctypes.c_double

    class stopoverEntry(ctypes.Structure):
        _fields_ = [("apId", ctypes.c_int), ("toO", ctypes.c_double), ("toD", ctypes.c_double)]

    stopover = f.stopover
    stopover.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    stopover.restype = stopoverEntry
    
    logger.info("Loaded all remaining C functions.")

if True: # useful discord.py functions
    async def send_success(ctx, text):
        embed = discord.Embed(description=f"{text}", color=0x6aaa4e)
        await ctx.send(embed=embed)

    async def send_error(ctx, text):
        embed = discord.Embed(description=f"{text}", color=0xf44336)
        await ctx.send(embed=embed)

    async def getPrefix(bot, message):
        try:
            g = message.guild
            if not g:
                return '$'
            with open(f"settings/guild/prefix/{g.id}.txt", 'r') as f:
                prefix = f.read()
                return prefix
        except:
            return '$'

bot = commands.Bot(command_prefix=getPrefix)

@bot.event
async def on_ready():
    logger.info("Bot is now ready.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await send_error(ctx, "Missing arguments. Use `$help` for proper command usage.")
    elif isinstance(error, commands.MissingRole) or isinstance(error, commands.MissingAnyRole):
        await send_error(ctx, "You do not have the required role(s) to run this command.")
    elif isinstance(error, commands.MissingPermissions):
        await send_error(ctx, "You do not have the required permission(s) to run this command.")
    elif isinstance(error, commands.NoPrivateMessage):
        await send_error(ctx, "This command cannot be used in a private message.")
    elif isinstance(error, commands.CheckFailure):
        await send_error(ctx, "You do not have access to this command.")
    else:
        logger.warning(str(error))

@commands.has_guild_permissions(administrator=True)
@bot.command()
async def prefix(ctx, pre):
    if pre:
        try:
            with open(f"settings/guild/prefix/{ctx.guild.id}.txt", 'w') as f: # creates new file if does not exist
                f.write(str(pre))
                await send_success(ctx, f"The command prefix has been updated to `{pre}`.")
        except:
            await send_error(ctx, f"Something went wrong. Please try again later.")
    else:
        await send_error(ctx, f"Prefix cannot be empty.")


f.benchmark()

bot.run(TOKEN)
# ***REMOVED***


# ┌────────────┐
# │ debug area │
# └────────────┘

# x = brutePaxConf(542, 197, 126, 600, 2, 19808, 100, False)
# print(x.yConf, x.jConf, x.fConf, x.maxIncome, x.planesPerRoute)
# x = stopover(2394, 563, 14500, 0)
# print(x.apId, x.toO, x.toD)
