import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='CRITICAL', milliseconds=True) # info
logger.info("Started.")

import discord # pip install discord.py
from discord.ext import commands
TOKEN = "***REMOVED***"
logger.info("Loaded discord.py.")

# standard modules
import os; os.system("python3 setup.py build_ext --inplace")
from helper_cy import *

if True: # useful discord.py functions and initialisation
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


bot.run(TOKEN)
x = input()
db.close()
print('MySQL connection closed.')

# ***REMOVED***


# ┌────────────┐
# │ debug area │
# └────────────┘

# x = brutePaxConf(542, 197, 126, 600, 2, 19808, 100, False)
# print(x.yConf, x.jConf, x.fConf, x.maxIncome, x.planesPerRoute)
# x = stopover(2394, 563, 14500, 0)
# print(x.apId, x.toO, x.toD)

### V3

import os
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()

    discord_token = os.getenv('DISCORD_TOKEN')
    am4tools_token = os.getenv('AM4TOOLS_TOKEN')
    if discord_token is None or am4tools_token is None:
        raise AssertionError('Discord and AM4Tools token required!')