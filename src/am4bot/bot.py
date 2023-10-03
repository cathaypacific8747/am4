import discord
from discord.ext.commands import Context, Bot
import am4utils
from .checks import ignore_pricealert, ignore_dm

from src.am4bot.config import Config

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix=Config.COMMAND_PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} on {", ".join([g.name for g in bot.guilds])}')
    am4utils.db.init()
    print(f'am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]} loaded')

    targets = ["admin-chat", "prvt-bugs-discussion", "prvt-bugs-open", "prvt-bugs-parked"]
    for guild in bot.guilds:
        for channel in guild.text_channels:
            print(channel)
            if channel.name in targets:
                print("****")
                async for message in channel.history(limit=50):
                    print(message.content)

async def warn_broken(ctx: Context):
    await ctx.send('We are experiencing with our hosting provider - many commands are broken right now and will be fixed hopefully <t:1694620800:R>')

@bot.command(help="shows botinfo")
@ignore_pricealert()
async def botinfo(ctx: Context):
    info = f'**AM4 ACDB bot (TEMPORARY)**\nMade by **favorit1** and **Cathay Express**\nDatabase and profit formula by **Scuderia Airlines**\nJoin this server: https://discord.gg/4tVQHtf'
    await ctx.send(info)
    await warn_broken(ctx)

# @bot.command(help = "Shows this command")
# @ignore_pricealert()
# @ignore_dm()
# async def help(ctx: Context, command='all'):
#     embed = discord.Embed(title="For more info on a command, use `help <command>`.", colour=discord.Colour.blue())
#     if command == 'all':
#         for cmd in bot.commands:
#             if not cmd.hidden and cmd.enabled:
#                 embed.add_field(name=cmd.name, value=f'```{cmd.short_doc}```', inline=False)
#     else:
#         try:
#             cmd = bot.get_command(command)
#             usage = f"${cmd.name}"
#             for param in cmd.clean_params:
#                 usage += f" <{param}>"
#             embed = discord.Embed(title=f'${command}', colour=discord.Colour.blue())
#             embed.add_field(name='Usage:', value=f'```{cmd.usage}```', inline=False)
#             embed.add_field(name='Description:', value=f'```{cmd.help}```', inline=False)
#         except:
#             embed = discord.Embed(title="Command not found!", colour=discord.Colour.blue())
#     await ctx.send(embed=embed)
#     await warn_broken(ctx)

# @bot.command(hidden=True)
# @ignore_pricealert()
# @ignore_dm()
# async def eval_24j32kj98f9dsaf9832rkjhica8s(ctx: Context, s: str):
#     eval(s)
#     await ctx.send("OK")

# @bot.command(hidden = True)
# @notPriceAlert()
# @notDM()
# async def login(ctx, *, airline_name):
#     airline_name = quote(airline_name)
#     use_id = False
#     try:
#         airline_name = int(airline_name)
#         use_id = True
#     except Exception:
#         pass
#     with urlopen(f'https://www.airline4.net/api/?access_token={Config.AM4_API_TOKEN}&user={airline_name}' if not use_id else f'https://www.airline4.net/api/?access_token=***REMOVED***&id={airline_name}') as file:
#         data = json.load(file)
#     if data['status']['request'] == 'success':
#         settings = discordSettings(discordUserId=ctx.author.id)
#         if use_id: 
#             settings.modifySetting('userid', airline_name)
#         else:
#             settings.removeSetting('userid')
        
#         if not use_id:
#             embed = discord.Embed(title = f"Is this you?", description = 'Please confirm that this is your airline by clicking on the <:yep:488368754070126594> button below. Otherwise, click on the <:nope:488368772571201536> button and follow the instructions on how to login correctly.', colour=discord.Colour(0x1f8de0))
            
#             hasIPO = bool(data['user']['share'])
#             allianceName = data['user']['alliance']
            
#             value  = f"**   Airline Name**: {data['user']['company']}\n"
#             value += f"**​         Rank**: {data['user']['rank']}\n"
#             value += f"**  ​      Level**: {data['user']['level']}\n"
#             value += f"**​       Mode**: {data['user']['game_mode']}\n"
#             value += f"**​Achievements**: {data['user']['achievements']}/81\n"
#             value += f"**     Founded**: {strftime('%d/%b/%Y', gmtime(data['user']['founded']))}\n"
#             cargoRep = '' if data['user']['cargo_reputation'] == 'N/A' else f", <:cargo:773841095896727573> {data['user']['cargo_reputation']}%"
#             value += f"**    Reputation**: <:pax:773841110271393833> {data['user']['reputation']}%{cargoRep}\n"
#             value += f"**   ​Routes/Fleet**: {data['user']['routes']}/{data['user']['fleet']}\n"
#             if hasIPO:
#                 value += f"**​      Share Value**: ${data['user']['share']:,.2f}\n"
#                 value += f"**​    Shares**: {data['user']['shares_sold']}/{data['user']['shares_sold']+data['user']['shares_available']}\n"
#             value += f"**​      Alliance**: {'---' if not allianceName else allianceName}\n"
#             embed.add_field(name='Basic Statistics', inline=False, value=value)
#             awards = "".join([f"`{strftime('%d/%b/%y', gmtime(award['awarded']))}` - {award['award']}\n" for award in data['awards']])
#             if awards:
#                 embed.add_field(name=':trophy: Awards', inline=False, value=awards)
            
#             message = await ctx.send(embed = embed)
#             await message.add_reaction('<:yep:488368754070126594>')
#             await message.add_reaction('<:nope:488368772571201536>')
#             await asyncio.sleep(0.1)
            
#             aut = ctx.message.author
#             def check(reaction, user):
#                 return user != bot.user and str(reaction.emoji) == '<:yep:488368754070126594>' or '<:nope:488368772571201536>' and reaction.message == message
#             try:
#                 reaction, user = await bot.wait_for('reaction_add', timeout = 60, check = check)
#             except asyncio.TimeoutError:
#                 await message.edit(content = "Login attempt timed out. Please try again.", embed = None)
#             else:
#                 if str(reaction.emoji) == '<:yep:488368754070126594>':
#                     pass
#                 elif str(reaction.emoji) == '<:nope:488368772571201536>':
#                     await message.edit(content = "To correct this issue, please use the $login command again, but this time using your **user ID**. This can be found in the in-game FAQ section, right at the top.", embed = None)
#                     return
#                 else:
#                     await message.edit(content = "Huh, this really shouldn't have happened.", embed = None)
#                     return
        
#         await ctx.author.edit(nick=data['user']['company'])

#         isRealism = data['user']['game_mode'] == 'Realism'
#         try:
#             await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name='Easy' if isRealism else 'Realism'))
#         except Exception:
#             pass
#         try:
#             await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name='Non AM'))
#         except Exception:
#             pass
        
#         await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Realism' if isRealism else 'Easy'))
#         if not use_id:
#             await message.delete()
#         await ctx.send(f'Welcome, **{data["user"]["company"]}**, to the AM4 Discord Server.\nHappy flying!')
#     else:
#         await ctx.send(content = f'Error: {data["status"]["description"]}')