V = 'v4.2.0'
info = f'**AM4 ACDB bot** {V}\nmade by **favorit1** and **Cathay Express**\ndatabase and profit formula by **Scuderia Airlines**'
ValidCogs = ['SettingsCog', 'DatabaseCog', 'AM4APICog', 'ShortcutsCog', 'AirportCog', 'AllianceCog', ]
AllowedGuilds = [697804430711586930, 473892865081081856]

# import modules and initialise stuff such as mysql first
from datetime import datetime, timedelta
from time import gmtime, time, strftime
from urllib.request import urlopen
from urllib.parse import quote
from sys import executable, argv
from os import execl, path, system
from random import randint
from copy import deepcopy
import math
import json
import csv
from checks import *
from DatabaseCog import profit, procargo
import mysql.connector
from SettingsCog import discordSettings
import asyncio
acdb = mysql.connector.connect(user='***REMOVED***',
                               passwd='***REMOVED***',
                               host='***REMOVED***',
                               database='***REMOVED***')
cursor = acdb.cursor(buffered = True)

# then start the bot-related actions
import discord
from discord.ext import commands, tasks
#intents = discord.Intents.default()
#intents.members = True
#intents.messages = True
bot = commands.Bot(command_prefix = '$', case_insensitive = True)
bot.remove_command('help')

@bot.event
async def on_ready():
    acotd = min(gmtime()[7], randint(1, 310))
    num = 0
    cursor.execute(f'SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type` FROM `am4bot`')
    for plane in cursor:
        if num == acotd:
            await bot.change_presence(activity = discord.Activity(type = 3, name = f'AC of the day: {plane[1]}'))
        num += 1
    
    for cog in ValidCogs:
        bot.load_extension(cog)
    
    print(f'ACDB Bot {V} is online, latency is {round(bot.latency * 1000)}ms')
    bot.resettime = gmtime()
    acdb.close()

@bot.event
async def on_command_error(ctx, error):    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Missing arguments. See $help for proper command usage.')
    elif isinstance(error, commands.MissingRole):
        await ctx.send(f'You do not have the required roles to use this command.')
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send(f'This command cannot be used in a private message.')
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"You're doing that too fast! Try again in {round(error.retry_after)} seconds.")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(f"Command has been temporarily disabled. We are working on enabling it again.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send(f"This command can't be used in Direct Messages.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CheckFailure):
        pass
    else:
        console = bot.get_channel(id = 475629813831565312)
        await console.send(f'Encountered an error:\nFrom message: {ctx.message.author.display_name}: `{ctx.message.content}`\nLink to message: {ctx.message.jump_url}\n```py\n{error}```<@&701415081547923516>')

'''
Public use:
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
$help
$login
$stats
$botinfo|version
$donate
$price
'''

@bot.command(hidden=True)
@modsOnly()
async def kickserver(ctx):
    for g in bot.guilds:
        gnin = g.id not in AllowedGuilds
        if gnin:
            await g.leave()
        await ctx.send(f'{g.id}: {"Left" if gnin else "pass"}')

@bot.command(help = "Shows this command")
@notPriceAlert()
@notDM()
async def help(ctx, command = 'all'):
    embed = discord.Embed(title = "For more info on a command, use \"$help <command>\".", colour = discord.Colour.blue())
    if command == 'all':
        for cmd in bot.commands:
            if not cmd.hidden and cmd.enabled:
                embed.add_field(name = cmd.name, value = f'```{cmd.short_doc}```', inline = False)
    else:
        try:
            cmd = bot.get_command(command)
            usage = f"${cmd.name}"
            for param in cmd.clean_params:
                usage += f" <{param}>"
            embed = discord.Embed(title = f'${command}', colour = discord.Colour.blue())
            embed.add_field(name = 'Usage:', value = f'```{cmd.usage}```', inline = False)
            embed.add_field(name = 'Description:', value = f'```{cmd.help}```', inline = False)
        except:
            embed = discord.Embed(title = "Command not found!", colour = discord.Colour.blue())
    await ctx.send(embed = embed)

@bot.command(hidden = True)
@notPriceAlert()
@notDM()
async def login(ctx, *, airlineName):
    airlineName = quote(airlineName)
    try:
        airlineName = int(airlineName)
        useid = True
    except:
        useid = False
    with urlopen(f'https://www.airline4.net/api/?access_token=***REMOVED***&user={airlineName}' if not useid else f'https://www.airline4.net/api/?access_token=***REMOVED***&id={airlineName}') as file:
        data = json.load(file)
    if data['status']['request'] == 'success':
        settings = discordSettings(discordUserId=ctx.author.id)
        if useid: 
            settings.modifySetting('userid', airlineName)
        else:
            settings.removeSetting('userid')
        
        if not useid:
            embed = discord.Embed(title = f"Is this you?", description = 'Please confirm that this is your airline by clicking on the <:yep:488368754070126594> button below. Otherwise, click on the <:nope:488368772571201536> button and follow the instructions on how to login correctly.', colour=discord.Colour(0x1f8de0))
            
            hasIPO = bool(data['user']['share'])
            allianceName = data['user']['alliance']
            
            value  = f"**   Airline Name**: {data['user']['company']}\n"
            value += f"**​         Rank**: {data['user']['rank']}\n"
            value += f"**  ​      Level**: {data['user']['level']}\n"
            value += f"**​       Mode**: {data['user']['game_mode']}\n"
            value += f"**​Achievements**: {data['user']['achievements']}/81\n"
            value += f"**     Founded**: {strftime('%d/%b/%Y', gmtime(data['user']['founded']))}\n"
            cargoRep = '' if data['user']['cargo_reputation'] == 'N/A' else f", <:cargo:773841095896727573> {data['user']['cargo_reputation']}%"
            value += f"**    Reputation**: <:pax:773841110271393833> {data['user']['reputation']}%{cargoRep}\n"
            value += f"**   ​Routes/Fleet**: {data['user']['routes']}/{data['user']['fleet']}\n"
            if hasIPO:
                value += f"**​      Share Value**: ${data['user']['share']:,.2f}\n"
                value += f"**​    Shares**: {data['user']['shares_sold']}/{data['user']['shares_sold']+data['user']['shares_available']}\n"
            value += f"**​      Alliance**: {'---' if not allianceName else allianceName}\n"
            embed.add_field(name='Basic Statistics', inline=False, value=value)
            awards = "".join([f"`{strftime('%d/%b/%y', gmtime(award['awarded']))}` - {award['award']}\n" for award in data['awards']])
            if awards:
                embed.add_field(name=':trophy: Awards', inline=False, value=awards)
            
            message = await ctx.send(embed = embed)
            await message.add_reaction('<:yep:488368754070126594>')
            await message.add_reaction('<:nope:488368772571201536>')
            await asyncio.sleep(0.1)
            
            aut = ctx.message.author
            def check(reaction, user):
                return user != bot.user and str(reaction.emoji) == '<:yep:488368754070126594>' or '<:nope:488368772571201536>' and reaction.message == message
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout = 60, check = check)
            except asyncio.TimeoutError:
                await message.edit(content = "Login attempt timed out. Please try again.", embed = None)
            else:
                if str(reaction.emoji) == '<:yep:488368754070126594>':
                    pass
                elif str(reaction.emoji) == '<:nope:488368772571201536>':
                    await message.edit(content = "To correct this issue, please use the $login command again, but this time using your **user ID**. This can be found in the in-game FAQ section, right at the top.", embed = None)
                    return
                else:
                    await message.edit(content = "Huh, this really shouldn't have happened.", embed = None)
                    return
        
        await ctx.author.edit(nick=data['user']['company'])

        isRealism = data['user']['game_mode'] == 'Realism'
        try:
            await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name='Easy' if isRealism else 'Realism'))
        except Exception:
            pass
        try:
            await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name='Non AM'))
        except Exception:
            pass
        
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Realism' if isRealism else 'Easy'))
        if not useid:
            await message.delete()
        await ctx.send(f'Welcome, **{data["user"]["company"]}**, to the AM4 Discord Server.\nHappy flying!')
    else:
        await ctx.send(content = f'Error: {data["status"]["description"]}')

@bot.command(help='Shows the number of command uses since last restart.', usage = '$stats')
@notPriceAlert()
@notDM()
async def stats(ctx):
    if ctx.guild != None: # not DM
        from DatabaseCog import infoC, compareC, searchC, seeallC
        from AM4APICog import airlineC, fleetC
        from ShortcutsCog import sheetC, websiteC
        from AirportCog import airportC, routesC, stopC
        await ctx.send(f'Usage (Since {strftime("%d/%b/%y at %H:%M UTC", bot.resettime)}):```ml\nInfo: ' + str(infoC) + '\nCompare: ' + str(compareC) + '\nSearch: ' + str(searchC) + '\nSeeall: ' + str(seeallC) + '\nPrice: ' + str(bot.priceC) + '\nWebsite: ' + str(websiteC) + '\nSheet: ' + str(sheetC) + '\nAirport: ' + str(airportC) + '\nAirline: ' + str(airlineC) + '\nFleet: ' + str(fleetC) + '\nStop: ' + str(stopC) + '\nRoutes: ' + str(routesC) + '```')

@bot.command(aliases = ['version'], hidden = True)
@notPriceAlert()
async def botinfo(ctx):
    await ctx.send(f'{info}\nJoin this server: https://discord.gg/4tVQHtf')

@bot.command(hidden = True)
@notPriceAlert()
async def donate(ctx):
    embed = discord.Embed(title = 'Support us by donating!', description = 'All proceeds will go towards running the ACDB bot and AM4Tools.com!', url = 'https://paypal.me/am4tools', colour = discord.Colour(0xfad563))
    embed.set_thumbnail(url = 'https://i5g3k7c2.stackpathcdn.com/assets/img/menu/points.png')
    embed.add_field(name = 'About the AM4 Tools Fund', value = "While we've been able to run these tools on our own, as popularity rose, so did the bills.\nWe do not want to resort to advertising, therefore we've decided to start a fund where we, as the devs, chip in, as well as enable others to donate.", inline = False)
    embed.add_field(name = 'What do I get if I donate?', value = "We promised ourselves, as well as the Developer, to keep our tools 100% free. Therefore we want the experience for donators and non-donators to be the same, except for a special role on the Discord server; no disadvantages to those, who don't donate.", inline = False)
    embed.add_field(name = 'Sounds great! How can I donate?', value = "Follow the link above (or go to paypal.me/am4tools), choose how much to donate then log in with your PayPal account. Be sure to include your in-game name in the note section, if you want us to recognize you.\nAny little helps! Thank You.")
    await ctx.send(embed = embed)

@bot.command(help='Ignores non #bot-spam warnings.', usage='$ignore')
async def ignore(ctx):
    pass

bot.priceC = 0
priceAlertId = 554503485765189642
botspamId    = 475885102178631680
async def parsePrice(costs, furtherErrorInfo, ctx):
    try:
        if not costs:
            raise RuntimeError('Missing arguments.')
        elif len(costs) > 2:
            raise RuntimeError('Too many arguments.')
        else:
            fuel, co2 = 9999, 9999
            try:
                for c in costs:
                    if c[0].lower() == 'f':
                        fuel = int(c[1:])
                    elif c[0].lower() == 'c':
                        co2  = int(c[1:])
                    else:
                        raise Exception()
            except ValueError:
                raise RuntimeError('Given price is not a number.')
            except Exception:
                raise RuntimeError('Formatting error.')
            else:
                return fuel, co2
    except RuntimeError as errorMessage:
        await ctx.send(f'{errorMessage} {furtherErrorInfo}')
        return 0, 0

@bot.command(help='Reports the current price, pinging PriceNotify.', usage='$price f<fuel price> c<co2 price>')
@notDM()
async def price(ctx, *costs):
    if ctx.message.channel.id == priceAlertId:
        furtherErrorInfo = f'See `$help price` for proper command usage in <#{botspamId}>.'
        try:
            async for m in bot.get_channel(priceAlertId).history():
                if m.author == bot.user and "Price sent by" in m.content:
                    now = datetime.utcnow()
                    intervalStart = now.replace(minute=(0 if now.minute < 30 else 30), second=0, microsecond=0)
                    if m.created_at < intervalStart:
                        break # the bot's last ping is earlier than the current earliest ping time.
                    else:
                        timeLeft = intervalStart + timedelta(minutes=30) - now
                        raise ValueError(f"You're doing that too fast! Try again in {timeLeft.total_seconds():.0f} seconds.")
            else:
                raise ValueError('Internal Error: last ping message not found.')
        except ValueError as errorMessage:
            await ctx.send(errorMessage)
        else:
            try:
                fuel, co2 = await parsePrice(costs, furtherErrorInfo, ctx)
                if fuel and co2: # if no errors
                    priceNotify, output = discord.utils.get(ctx.guild.roles, name='PriceNotify'), ''
                    if fuel != 9999:
                        output += f'Fuel price is ${fuel}. '
                    if co2 != 9999:
                        output += f'CO2 price is ${co2}. '
                    
                    if (fuel <= 900 or co2 <= 140) and not kill:
                        await priceNotify.edit(mentionable=True)
                        await ctx.send(f'{output}{priceNotify.mention} (Price sent by {ctx.message.author.mention})')
                        await priceNotify.edit(mentionable=False)
                    else:
                        await ctx.send(f'{output} (Price sent by {ctx.message.author.mention})')

                    # custom for qatar
                    if (fuel <= 750 or co2 <= 140):
                        print('Send start.')
                        qatar = bot.get_user(430192751779250176)
                        await qatar.send(f'{output} (Price sent by {ctx.message.author.mention})')
                        print('Send end.')

                    with open('ass.json', 'r+') as f:
                        oldData = json.load(f)
                        oldData[f'{time()}'] = {'fuel': f'{fuel}', 'co2': f'{co2}'}
                        f.seek(0)
                        json.dump(oldData, f)
                        f.truncate()
                    
                    await ctx.message.delete()
            except:
                pass

'''
Mod use:
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
$priceUpdate
'''

@bot.command(hidden=True)
@modsOnly()
async def priceUpdate(ctx, *costs):
    if ctx.message.channel.id == priceAlertId:
        furtherErrorInfo = ''
        try:
            async for m in bot.get_channel(priceAlertId).history():
                if m.author == bot.user and "Price sent by" in m.content:
                    now = datetime.utcnow()
                    intervalStart = now.replace(minute=(0 if now.minute < 30 else 30), second=0, microsecond=0)
                    if m.created_at > intervalStart:
                        lastMessage = m
                        break # the bot ping time is greater than the current interval's start time, so it is avaliable for editing.
                    else:
                        raise ValueError("The price you're trying to update has already expired. Use `$price` to report the current price instead.")
            else:
                raise ValueError('Internal Error: last ping message not found.')
        except ValueError as errorMessage:
            await ctx.send(errorMessage)
        else:
            try:
                nowFuel, nowCo2 = await parsePrice(costs, furtherErrorInfo, ctx)
                if nowFuel and nowCo2: # no errors involved.
                    oldFuel, oldCo2 = 9999, 9999
                    priceStrings = lastMessage.content.split('. ')[:-1]
                    for p in priceStrings:
                        if p.startswith('Fuel price is $'):
                            oldFuel = int(p.replace('Fuel price is $', ''))
                        else:
                            oldCo2 = int(p.replace('CO2 price is $', ''))

                    newFuel = nowFuel if nowFuel != 9999 else oldFuel
                    newCo2 = nowCo2 if nowCo2 != 9999 else oldCo2

                    priceNotify, output = discord.utils.get(ctx.guild.roles, name='PriceNotify'), ''
                    if newFuel != 9999:
                        output += f'Fuel price is ${newFuel}. '
                    if newCo2 != 9999:
                        output += f'CO2 price is ${newCo2}. '
                    
                    oldMentions = lastMessage.content.split('(Price sent by ')[1].split(')')[0]

                    if (newFuel <= 900 or newCo2 <= 140) and not kill:
                        await lastMessage.edit(content=f'{output}{priceNotify.mention} (Price sent by {oldMentions}, {ctx.message.author.mention})')
                    else:
                        await lastMessage.edit(content=f'{output} (Price sent by {oldMentions}, {ctx.message.author.mention})')

                    with open('ass.json', 'r+') as f:
                        oldData = json.load(f)
                        oldData[sorted(list(oldData))[-1]] = {'fuel': f'{newFuel}', 'co2': f'{newCo2}'}
                        f.seek(0)
                        json.dump(oldData, f)
                        f.truncate()

                    await ctx.message.delete()
            except:
                pass

'''
GuideDev use:
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
$killswitch|kill
$restart|reset
$recon|recon
$resetcool
$reload
$unload|pause
$load
$clearconsole
'''

kill = False
@bot.command(hidden=True, aliases = ['kill'])
@guideDevsOnly()
async def killswitch(ctx):
    global kill
    kill = not kill
    await ctx.send('Notifications killed!')

@bot.command(aliases = ['reset'], hidden = True)
@guideDevsOnly()
async def restart(ctx):
    execl(executable, path.abspath(__file__), * argv)

@bot.command(aliases = ['recon'], hidden = True)
@guideDevsOnly()
async def reconnect(ctx):
    acdb.reconnect(attempts = 5, delay = 0.5)

@bot.command(hidden = True)
@guideDevsOnly()
async def resetcool(ctx):
    price.reset_cooldown(ctx)
    await ctx.send('Cooldown has been reset!')

@bot.command(hidden = True)
@guideDevsOnly()
async def reload(ctx, extension='all'):
    if extension == 'all':
        bot.resettime = gmtime()
        for cog in list(bot.extensions):
            bot.reload_extension(cog)
        await ctx.send('All extensions reloaded.')
    else:
        bot.unload_extension(extension)
        bot.load_extension(extension)
        await ctx.send(f'{extension} has been reloaded.')
    
@bot.command(aliases = ['pause'], hidden = True)
@guideDevsOnly()
async def unload(ctx, extension = 'all'):
    if extension == 'all':
        for cog in list(bot.extensions):
            bot.unload_extension(cog)
        await ctx.send('All extensions have been unloaded.')
    else:
        bot.unload_extension(extension)
        await ctx.send(f'{extension} has been unloaded.')

@bot.command(hidden = True)
@guideDevsOnly()
async def load(ctx, extension = 'valid extensions'):
    if extension == 'valid extensions':
        for cog in ValidCogs:
            try: bot.load_extension(cog)
            except commands.ExtensionAlreadyLoaded: pass
        await ctx.send('All stock extensions loaded.')
    else:
        bot.load_extension(extension)
        await ctx.send(f'{extension} has been loaded!')

@bot.command(hidden=True)
@guideDevsOnly()
async def clearConsole(ctx):
    system('clear')

bot.run('***REMOVED***')
paused = False
