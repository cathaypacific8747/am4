V = 'v4.1.5'
botinfo = f'**AM4 ACDB bot** {V}\nmade by **favorit1**, maintained by **Cathay Express**\ndatabase and profit formula by **Scuderia Airlines**'

ValidCogs = ['DatabaseCog', 'AM4APICog', 'ShortcutsCog', 'AirportCog']

from discord.ext import commands, tasks
from time import gmtime, time, strftime
from urllib.request import urlopen
from urllib.parse import quote
from sys import executable, argv
from os import execl, path, system
from random import randint
from copy import deepcopy
import mysql.connector
import discord
import math
import json
import csv

bot = commands.Bot(command_prefix = '$', case_insensitive = True)
bot.remove_command('help')

acdb = mysql.connector.connect(user='***REMOVED***',
                               passwd='***REMOVED***',
                               host='***REMOVED***',
                               database='***REMOVED***')

cursor = acdb.cursor(buffered = True)

def restart_program():
    execl(executable, path.abspath(__file__), * argv)

bot.priceC = 0
        
@bot.event
async def on_ready():
    if gmtime()[7] >= 311:
        acotd = randint(1, 310)
    else:
        acotd = gmtime()[7]
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
    else:
        console = bot.get_channel(id = 475629813831565312)
        await console.send(f'Encountered an error:\nFrom message: {ctx.message.author.display_name}: `{ctx.message.content}`\nLink to message: {ctx.message.jump_url}\n```py\n{error}```<@&701415081547923516>')

from DatabaseCog import profit, procargo

@bot.command(help = "Shows this command")
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
async def login(ctx, *, airline):
    if not '%' in airline:
        airline = quote(airline)
    with urlopen(f'https://www.airline4.net/api/?access_token=***REMOVED***&user={airline}') as file:
        data = json.load(file)
    if data['status']['request'] == 'success':
        await ctx.author.edit(nick = data['user']['company'])
        if data['user']['game_mode'] == 'Realism':
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Realism'))
        else:
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Easy'))
        await ctx.send(f'Welcome, **{data["user"]["company"]}**, to the AM4 Discord Server.\nHappy flying!')
    else:
        await ctx.send(content = f'Error: {data["status"]["description"]}')

def correct_channel(ctx):
    return ctx.message.channel.id == 554503485765189642, 484644663471636481
try:
    with open('ass.json') as infile:
        shit = json.load(infile)
except:
    shit = None
    print('PGS not enabled.')

kill = False

@bot.command(help='Reports the current price, pinging PriceNotify', usage = '$price f<fuel price> c<co2 price>')
@commands.check(correct_channel)
@commands.cooldown(1, 900)
async def price(ctx, *cost):
    bot.priceC += 1
    role = discord.utils.get(ctx.guild.roles, name = 'PriceNotify')
    if len(cost) > 2:
        await ctx.send("Too many numbers in there!")
        price.reset_cooldown(ctx)
    elif len(cost) == 0:
        await ctx.send(f'Missing arguments. See $help for proper command usage.')
        price.reset_cooldown(ctx)
    else:
        output = f""
        fuel = 9999
        co2 = 9999
        for i in cost:
            if i[0] == 'f':
                try:
                    fuel = int(i.replace('f', ''))
                    output += f"Fuel price is ${fuel}. "
                except:
                    await ctx.send("Given price isn't a number!")
                    price.reset_cooldown(ctx)
            elif i[0] == 'c':
                try:
                    co2 = int(i.replace('c', ''))
                    output += f"CO2 price is ${co2}. "
                except:
                    await ctx.send("Given price isn't a number!")
                    price.reset_cooldown(ctx)
            else:
                await ctx.send("Formatting error.")
                price.reset_cooldown(ctx)
        if fuel <= 900 or co2 <= 140 and not kill:
            await role.edit(mentionable = True)
            await discord.utils.get(ctx.guild.channels, id = 554503485765189642).send(output + role.mention + f" (Price sent by {ctx.message.author.mention})")
            await role.edit(mentionable = False)
        elif output != f"":
            await discord.utils.get(ctx.guild.channels, id = 554503485765189642).send(output + f"(Price sent by {ctx.message.author.mention})")
        try:
            shit[f'{time()}'] = {'fuel' : f'{fuel}', 'co2' : f'{co2}'}
            with open('ass.json', 'w') as outfile:
                json.dump(shit, outfile)
        except:
            pass
        await ctx.message.delete()

kill = False
@bot.command(hidden=True, aliases = ['kill'])
@commands.has_role(646148607636144131)
async def killswitch(ctx):
    global kill
    kill = not kill
    await ctx.send('Notifications killed!')

@bot.command(help='Shows the number of command uses since last restart.', usage = '$stats')
async def stats(ctx):
    if ctx.guild != None: # not DM
        from DatabaseCog import infoC, compareC, searchC, seeallC
        from AM4APICog import airlineC, fleetC
        from ShortcutsCog import sheetC, websiteC
        from AirportCog import airportC, routesC, stopC
        await ctx.send(f'Usage (Since {strftime("%d/%b/%y at %H:%M UTC", bot.resettime)}):```ml\nInfo: ' + str(infoC) + '\nCompare: ' + str(compareC) + '\nSearch: ' + str(searchC) + '\nSeeall: ' + str(seeallC) + '\nPrice: ' + str(bot.priceC) + '\nWebsite: ' + str(websiteC) + '\nSheet: ' + str(sheetC) + '\nAirport: ' + str(airportC) + '\nAirline: ' + str(airlineC) + '\nFleet: ' + str(fleetC) + '\nStop: ' + str(stopC) + '\nRoutes: ' + str(routesC) + '```')
        
@bot.command(aliases = ['reset'], hidden = True)
@commands.has_role(646148607636144131)
async def restart(ctx):
    restart_program()

@bot.command(aliases = ['recon'], hidden = True)
@commands.has_role(646148607636144131)
async def reconnect(ctx):
    acdb.reconnect(attempts = 5, delay = 0.5)

@bot.command(hidden = True)
@commands.has_role(646148607636144131)
async def resetcool(ctx):
    price.reset_cooldown(ctx)
    await ctx.send('Cooldown has been reset!')

@bot.command(aliases = ['botinfo'], hidden = True)
async def version(ctx):
    await ctx.send(botinfo + '\nJoin our bot support server: https://discord.gg/4tVQHtf')

@bot.command(hidden = True)
async def donate(ctx):
    embed = discord.Embed(title = 'Support us by donating!', description = 'All proceeds will go towards running the ACDB bot and AM4Tools.com!', url = 'https://paypal.me/am4tools', colour = discord.Colour(0xfad563))
    embed.set_thumbnail(url = 'https://i5g3k7c2.stackpathcdn.com/assets/img/menu/points.png')
    embed.add_field(name = 'About the AM4 Tools Fund', value = "While we've been able to run these tools on our own, as popularity rose, so did the bills.\nWe do not want to resort to advertising, therefore we've decided to start a fund where we, as the devs, chip in, as well as enable others to donate.", inline = False)
    embed.add_field(name = 'What do I get if I donate?', value = "We promised ourselves, as well as the Developer, to keep our tools 100% free. Therefore we want the experience for donators and non-donators to be the same, except for a special role on the Discord server; no disadvantages to those, who don't donate.", inline = False)
    embed.add_field(name = 'Sounds great! How can I donate?', value = "Follow the link above (or go to paypal.me/am4tools), choose how much to donate then log in with your PayPal account. Be sure to include your in-game name in the note section, if you want us to recognize you.\nAny little helps! Thank You.")
    await ctx.send(embed = embed)
        
@bot.command(hidden = True)
@commands.has_role(646148607636144131)
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
@commands.has_role(646148607636144131)
async def unload(ctx, extension = 'all'):
    if extension == 'all':
        for cog in list(bot.extensions):
            bot.unload_extension(cog)
        await ctx.send('All extensions have been unloaded.')
    else:
        bot.unload_extension(extension)
        await ctx.send(f'{extension} has been unloaded.')

@bot.command(hidden = True)
@commands.has_role(646148607636144131)
async def load(ctx, extension = 'valid extensions'):
    print('bitch1')
    if extension == 'valid extensions':
        print('bitch2')
        for cog in ValidCogs:
            print('bitch3')
            try: bot.load_extension(cog)
            except commands.ExtensionAlreadyLoaded: pass
            print('bitch4')
        await ctx.send('All stock extensions loaded.')
    else:
        print('bitch5')
        bot.load_extension(extension)
        print('bitch6')
        await ctx.send(f'{extension} has been loaded!')

@bot.command(hidden=True)
@commands.has_role(646148607636144131)
async def clearConsole(ctx):
    system('clear')

bot.run('***REMOVED***')

paused = False