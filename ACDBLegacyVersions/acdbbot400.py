V = 'v4.0.0'
botinfo = f'**AM4 ACDB bot** {V}\nmade by **favorit1**, contributed by **Cathay Express**\ndatabase and profit formula by **Scuderia Airlines**'

ValidCogs = ['DatabaseCog', 'AM4APICog', 'ShortcutsCog', 'AirportCog']

from discord.ext import commands, tasks
from time import gmtime, time, strftime
from urllib.request import urlopen
from urllib.parse import quote
from sys import executable, argv
from os import execl, path
from random import randint
from copy import deepcopy
import mysql.connector
import discord
import math
import json
import csv

bot = commands.Bot(command_prefix = '$')
acdb = mysql.connector.connect(user='***REMOVED***',
                               passwd='***REMOVED***',
                               host='***REMOVED***',
                               database='***REMOVED***')

cursor = acdb.cursor(buffered = True)

def restart_program():
    execl(executable, path.abspath(__file__), * argv)

bot.priceC = 0
def counter(cmd):
    #if cmd == 'info': bot.infoC += 1
    #elif cmd == 'compare': bot.compareC += 1
    #elif cmd == 'search': bot.searchC += 1
    #if cmd == 'seeall': bot.seeallC += 1
    if cmd == 'price': bot.priceC += 1
    #elif cmd == 'website': bot.websiteC += 1
    #elif cmd == 'sheet': bot.sheetC += 1
    #elif cmd == 'airport': bot.airportC += 1
    #elif cmd == 'fleet': bot.fleetC += 1
    #elif cmd == 'airline': bot.airlineC += 1
        
@bot.event
async def on_ready():
    global ac, ac1, pro, pro1, pro2
    if gmtime()[7] >= 311:
        acotd = randint(1, 310)
    else:
        acotd = gmtime()[7]
    num = 0
    cursor.execute(f'SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type` FROM `am4bot`')
    for plane in cursor:
        if num == acotd:
            ac = ac1 = plane
            await bot.change_presence(activity = discord.Activity(type = 3, name = f'AC of the day: {plane[1]}'))
        num += 1
    for cog in ValidCogs:
        bot.load_extension(cog)
    print(f'ACDB Bot {V} is online, latency is {round(bot.latency * 1000)}ms')
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

from DatabaseCog import profit, procargo

ac = ac1 = ac2 = pro1 = pro2 = msg = pro = embed = ps = cs = rs = ss = fs = es = fr = dr = pr = fe = de = pe = ''

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

@bot.command(help='Reports the current price, pinging PriceNotify')
@commands.check(correct_channel)
@commands.cooldown(1, 900)
async def price(ctx, *cost):
    counter('price')
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

@bot.command(help='Shows the number of command uses since last restart.')
async def stats(ctx):
    from DatabaseCog import infoC, compareC, searchC, seeallC
    from AM4APICog import airlineC, fleetC
    from ShortcutsCog import sheetC, websiteC
    from AirportCog import airportC, routesC, stopC
    await ctx.send('Usage (Since Last Reset):```ml\nInfo: ' + str(infoC) + '\nCompare: ' + str(compareC) + '\nSearch: ' + str(searchC) + '\nSeeall: ' + str(seeallC) + '\nPrice: ' + str(bot.priceC) + '\nWebsite: ' + str(websiteC) + '\nSheet: ' + str(sheetC) + '\nAirport: ' + str(airportC) + '\nAirline: ' + str(airlineC) + '\nFleet: ' + str(fleetC) + '\nStop: ' + str(stopC) + '\nRoutes: ' + str(routesC) + '```')
    
@bot.command(aliases=['reset'], hidden = True)
@commands.has_role(646148607636144131)
async def restart(ctx):
    restart_program()

@bot.command(aliases=['recon'], hidden = True)
@commands.has_role(646148607636144131)
async def reconnect(ctx):
    acdb.reconnect(attempts = 5, delay = 0.5)

@bot.command(hidden=True)
@commands.has_role(646148607636144131)
async def resetcool(ctx):
    price.reset_cooldown(ctx)
    await ctx.send('Cooldown has been reset!')

@bot.command(aliases = ['botinfo'], hidden = True)
async def version(ctx):
    if paused == False:
        await ctx.send(botinfo + '\nJoin our bot support server: https://discord.gg/4tVQHtf')

paused = False
@bot.command(hidden=True)
@commands.has_role(646148607636144131)
async def load(ctx, extension = 'valid extensions'):
    if extension == 'valid extensions':
        for cog in ValidCogs:
            try: bot.load_extension(cog)
            except: pass
        await ctx.send('All stock extensions loaded.')
    else:
        try: bot.load_extension(extension)
        except: await ctx.send('Extension not found.')
        await ctx.send(f'{extension} has been loaded!')
        
@bot.command(hidden=True)
@commands.has_role(646148607636144131)
async def reload(ctx):
    for cog in list(bot.extensions):
        bot.reload_extension(cog)
    await ctx.send('All extensions reloaded')
    
@bot.command(aliases=['pause'], hidden=True)
@commands.has_role(646148607636144131)
async def unload(ctx, extension = 'all'):
    if extension == 'all':
        for cog in list(bot.extensions):
            bot.unload_extension(cog)
        await ctx.send('All extensions have been unloaded.')
    else:
        bot.unload_extension(extension)
        await ctx.send(f'{extension} has been unloaded.')
    
bot.run('***REMOVED***')
