V = 'v4.0.0 InDev'
botinfo = f'**AM4 ACDB bot** {V}\nmade by **favorit1**, maintained by **Cathay Express**\ndatabase and profit formula by **Scuderia Airlines**'

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

#@bot.event
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

### STOPOVER ###
# with open('data/ap-indexed-radians.csv', newline='', encoding='utf-8-sig') as f:
#     global airports
#     airports = list(csv.reader(f))

# with open('data/ac-indexed.csv', newline='', encoding='utf-8-sig') as f:
#     global aircrafts
#     aircrafts = list(csv.reader(f))

# def calcCargoConfig(lh, maxCap, fPerDay):
#     maxCap = int(maxCap)
#     l = int(lh[0]) / int(fPerDay)
#     h = int(lh[1]) / int(fPerDay)

#     lCap = maxCap * 0.7 if (int(lh[0]) / 0.7 > maxCap * int(fPerDay)) else l # if demand > capacity, set full large.
#     lPct = int(lCap / maxCap / 0.7 * 100) / 100
#     hCap = maxCap * (1 - lPct)
#     if h >= hCap: # if there is excess demand
#         return [lPct, int(100 * (1 - lPct)) / 100]
#     else: # hDemand too small, depleted easily, return nothing
#         return [0, 0]

# def calcFirstPrioritizedSeats(yjf, maxSeats, fPerDay):
#     y = int(yjf[0]) / int(fPerDay)
#     j = int(yjf[1]) / int(fPerDay)
#     f = int(yjf[2]) / int(fPerDay)

#     fS = int(maxSeats / 3) if (f*3 > maxSeats) else int(f)
#     jS = int((maxSeats - (fS*3)) / 2) if ((j*2 + f*3) > maxSeats) else int(j)
#     yS = maxSeats - fS*3 - jS*2

#     if (yS * fPerDay) < y:
#         return [yS, jS, fS]
#     else:
#         return [0, 0, 0]

# def distanceCoor(lat1, lon1, lat2, lon2): # radians
#     return 12742 * math.asin(math.sqrt(math.pow(math.sin((lat2-lat1) / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin((lon2-lon1) / 2), 2)))

# def findStopover(oName, dName, shortName, isRealism=False): # None = malformed input
#     o, d, range, rwyReq = [], [], -1, 0 # in case if airport is not found

#     ##  get aircraftRange and minRwy whenever possible  ##
#     for ac in aircrafts:
#         if ac[1] == shortName:
#             range = int(ac[12])
#             isCargo = bool(int(ac[19]))
#             if isRealism:
#                 rwyReq = int(ac[11]) # if easy, the rwy is unlimited as set by default.
#             break

#     ##  get input airport details  ##
#     for ap in airports:
#         # IATA
#         if ap[3] == oName: o = ap
#         if ap[3] == dName: d = ap
#         # ICAO
#         if ap[4] == oName: o = ap
#         if ap[4] == dName: d = ap
#         # expected to take more computing power, but allows different inputs;
#         # i.e. LHR > YSSY returns values.

#     if o != [] and d != [] and range != -1:
#         # only if there aren't inputErrors:
#         stpvrCandidates = deepcopy(airports)
#         for ap in stpvrCandidates:
#             try:
#                 oD = distanceCoor(float(o[7]), float(o[8]), float(ap[7]), float(ap[8])) # origin > thisAirport distance
#                 dD = distanceCoor(float(d[7]), float(d[8]), float(ap[7]), float(ap[8])) # destnt > thisAirport distance
                
#                 if oD < 100 or dD < 100: raise ValueError() # location is the hub/ below game lower distance limit
#                 if oD > range or dD > range: raise ValueError() # aircraft's range too short
#                 if rwyReq > int(ap[5]): raise ValueError() # aircraft's rwy too short

#                 ap.extend([oD, dD])
#             except ValueError:
#                 ap.extend([float('inf'), float('inf')]) # set both at max, such that it will be at the bottom

#         stpvrCandidates.sort(key=lambda x:x[9]+x[10])

#         stpvrCandidates = stpvrCandidates[0]
#         if stpvrCandidates[9] + stpvrCandidates[9] == float('inf'):
#             return 'UNREACHABLE'
#         else:
#             stpvrCandidates.extend([o[1], o[7], o[8], d[1], d[7], d[8], isCargo, range])
#             return stpvrCandidates
#     else:
#         return None

# def tickets(distance, isRealism=False, isCargo=False):
#     if isCargo:
#         if isRealism:
#             l = math.floor(((0.000776321822039374 * distance + 0.860567600367807000) - 0.01) * 1.10 * 100) / 100
#             h = math.floor(((0.000517742799409248 * distance + 0.256369915396414000) - 0.01) * 1.08 * 100) / 100
#         else:
#             l = math.floor(((0.000948283724581252 * distance + 0.862045432642377000) - 0.01) * 1.10 * 100) / 100
#             h = math.floor(((0.000689663577640275 * distance + 0.292981124272893000) - 0.01) * 1.08 * 100) / 100
#         return [l, h]
#     else:
#         if isRealism:
#             y = math.floor((0.3 * distance + 150) * 1.10 / 10) * 10
#             j = math.floor((0.6 * distance + 500) * 1.08 / 10) * 10
#             f = math.floor((0.9 * distance + 1000) * 1.06 / 10) * 10
#         else:
#             y = math.floor((0.4 * distance + 170) * 1.10 / 10) * 10
#             j = math.floor((0.8 * distance + 560) * 1.08 / 10) * 10
#             f = math.floor((1.2 * distance + 1200) * 1.06 / 10) * 10
#         return [y, j, f]

# @bot.command(help='Finds the most distance-efficient stopover given inputs of aircraft, origin and destination.', brief='Finds the most distance-efficient stopover.')
# async def stop(ctx, oName, dName, shortACname):
#     if not paused:
#         realismRole = discord.utils.get(ctx.guild.roles, name='Realism')
#         if realismRole in ctx.author.roles: 
#             isRealism = True # user is Realism
#             subheading = '**Realism**'
#         else:
#             isRealism = False
#             subheading = '**Easy**'

#         stpvr = findStopover(oName.upper(), dName.upper(), shortACname.lower(), isRealism)
#         if stpvr == None:
#             await ctx.send('Wrong inputs. See $help for proper command usage.')
#         else:
#             if stpvr != 'UNREACHABLE':
#                 isCargo, isMobile = stpvr[17], ctx.author.is_on_mobile()
#                 embed = discord.Embed(
#                     title=stpvr[11] + ' -- ' + stpvr[14], 
#                     colour=discord.Colour.dark_blue()
#                 )
#                 d = math.ceil(distanceCoor(float(stpvr[12]), float(stpvr[13]), float(stpvr[15]), float(stpvr[16])))
#                 t = tickets(d, isRealism, isCargo)

#                 if 1: # display details, don't mind me, just to make it collapsible
#                     value = '```ml\n'
#                     value += '    IATA: ' + stpvr[3] + '\n'
#                     value += '    ICAO: ' + stpvr[4] + '\n'
#                     if isRealism:
#                         value += '  Runway: ' + stpvr[5] + ' FT\n'
#                     if isMobile:
#                         value += 'Location: ' + stpvr[1] + ',\n'
#                         value += '          ' + stpvr[2] + '\n'
#                         value += 'Distance: ' + str(d) + ' KM' + '\n'
#                         if isCargo:
#                             value += ' Tickets: L [' + str(t[0]) + ']\n'
#                             value += '          H [' + str(t[1]) + ']```'
#                         else:
#                             value += ' Tickets: Y [' + str(t[0]) + ']\n'
#                             value += '          J [' + str(t[1]) + ']\n'
#                             value += '          F [' + str(t[2]) + ']```'
#                     else: # desktop
#                         value += 'Location: ' + stpvr[1] + ', ' + stpvr[2] + '\n'
#                         value += 'Distance: ' + str(d) + ' KM' + '\n'
#                         if isCargo: value += ' Tickets: L $[' + str(t[0]) + '], H $[' + str(t[1]) + ']```'
#                         else:       value += ' Tickets: Y $[' + str(t[0]) + '], J $[' + str(t[1]) + '], F $[' + str(t[2]) + ']```'

#                     embed.add_field(name=subheading, value=value)
#                     embed.set_footer(text="Formulae provided by Scuderia Airlines.")
#                 await ctx.send(embed=embed)
#             else:
#                 msg = '‎\u200B\n'
#                 msg += 'There are **no possible stopovers** for this route, in '+subheading+' mode.'
#                 await ctx.send(msg)

# @bot.command(help='Shows the most profitable routes given the maximum distance and hub.\n For training-points-enhanced cargo load (1.06x capacity), add a "+" at the back of the <shortACname>.', brief='Finds the most profitable routes.')
# async def routes(ctx, airportName, shortACname, targetDistance, flightsPerDay):
#     if not paused:
#         capacityMod = 1.06 if '+' in shortACname else 1
#         shortACname = shortACname.replace('+', '').lower()
#         airportName = airportName.upper()

#         isRealism = discord.utils.get(ctx.guild.roles, name='Realism') in ctx.author.roles # checks whether the user is Realism or not

#         o, range, rwyReq, needsStopover = [], -1, 0, False # in case if airport is not found
#         ##  get aircraftRange and minRwy whenever possible  ##
#         for ac in aircrafts:
#             if ac[1] == shortACname:
#                 fullName = ac[2] + ' ' + ac[3]
#                 range = int(ac[12])
#                 isCargo = bool(int(ac[19]))
#                 capacity = int(ac[10]) * capacityMod
#                 if isRealism: rwyReq = int(ac[11]) # if easy, the rwy is unlimited as set by default.
#                 break

#         for ap in airports:
#             if ap[3] == airportName or ap[4] == airportName: 
#                 o = ap # iata/icao recognisation
#                 break

#         if o == [] or range == -1:
#             await ctx.send('Airport and/or aircraft not found. See $help for proper command usage.')
#         else:
#             if int(targetDistance) > range * 2:
#                 msg = f':warning:**Warning: **Target Distance ({targetDistance} km) is larger than the maximum stopover range of the aircraft ({range*2} km).' + '\n'
#                 msg += f'Now assuming your target distance to be **{range*2}** km.'
#                 await ctx.send(msg)
#                 targetDistance = range * 2
#             if int(targetDistance) > range:
#                 # stopovers are needed, so set the flag
#                 needsStopover = True

#             with open(f'data/dist/{o[0]}.csv', newline='', encoding='utf-8-sig') as f:
#                 data, filtered = list(csv.reader(f)), []
#                 embed = discord.Embed(
#                     title=f'{fullName} departing {o[1]}, {o[2]}',
#                     colour=discord.Colour.dark_blue()
#                 )

#                 for d in data:
#                     if int(d[9]) <= int(targetDistance) and int(d[8]) >= rwyReq:
#                         filtered.append(d)

#                 for f in filtered:
#                     try:
#                         if isCargo:
#                             cargoCfg = calcCargoConfig([round(int(f[1])*500, -3), round(int(f[2])*1000, -3)], int(capacity), int(flightsPerDay)) # configuration in decimal percentages
#                             ticketP = tickets(int(f[9]), isRealism, True) # cargo prices
#                             maxIncome = ticketP[0] * (cargoCfg[0]*capacity*0.7) + ticketP[1] * (cargoCfg[1]*capacity)
#                             f.extend([maxIncome, cargoCfg, ticketP])
#                         else:
#                             paxCfg = calcFirstPrioritizedSeats([int(f[1]), int(f[2]), int(f[3])], capacity, int(flightsPerDay)) # pax in pure seats
#                             ticketP = tickets(int(f[9]), isRealism, False) # pax prices
#                             maxIncome = ticketP[0]*paxCfg[0] + ticketP[1]*paxCfg[1] + ticketP[2]*paxCfg[2]
#                             f.extend([maxIncome, paxCfg, ticketP])
#                     except:
#                         f.extend([0, [0, 0, 0], [0, 0, 0]])

#                 filtered.sort(key=lambda x:x[10], reverse=True)
#                 counter = 0

#                 for f in filtered:
#                     if int(f[10]) > 0: # income is +ve
#                         val = '```ml\n'
#                         try:
#                             if needsStopover:
#                                 stop = findStopover(o[3], f[6], shortACname, isRealism) # calculate the stopover for that route
#                                 if stop != None and stop != 'UNREACHABLE': # add stopover to display
#                                     val += f'Stopover: {stop[1]}, {stop[2]}' + '\n'
#                                     val += f'          {stop[3]} | {stop[4]}' + '\n'
#                                 else:
#                                     raise ValueError('noStopovers')

#                             if isCargo:
#                                 val += f'  Demand: L [{round(1000 * round(int(f[1])*0.5))}], H [{round(1000 * int(f[2]))}]' + '\n'
                                
#                                 val += f'  Config: L [{int(f[11][0] * 100)}%], H [{int(f[11][1] * 100)}%]' + '\n'
#                                 val += f' Tickets: L $[{f[12][0]}], H $[{f[12][1]}]' + '\n'
#                             else:
#                                 val += f'  Demand: Y [{f[1]}], J [{f[2]}], F [{f[3]}]' + '\n'
#                                 val += f'  Config: Y [{f[11][0]}], J [{f[11][1]}], F [{f[11][2]}]' + '\n'
#                                 val += f' Tickets: Y $[{f[12][0]}], J $[{f[12][1]}], F $[{f[12][2]}]' + '\n'

#                             if isRealism: 
#                                 val += f'  Runway: {f[8]} FT' + '\n'

#                             val += f'Distance: {f[9]} KM' + '\n'                
#                             val += f'  Income: $ {int(f[10]):,d}' + '\n'
#                             val += '```'

#                             embed.add_field(name=f'**{f[4]}**, {f[5]}\n{f[6]} | {f[7]}', value=val, inline=False)
#                             counter += 1
#                         except:
#                             pass # don't even show the route if stopovers aren't possible
#                     if counter > 5:
#                         break # stop the loop, as it has already displayed over 5 results
#                         # just in case the possible routes are less than 5, the for loop would've finished already
#                 if counter == 0:
#                     embed.add_field(name='Error', value='There are no profitable routes.')
#                 embed.set_footer(text="Database and formulae provided by Scuderia Airlines and Cathay Express.")
#                 await ctx.send(embed=embed)

## BOT MANAGEMENT ##

# @bot.command(hidden=True)
# async def testing(ctx):
#     yEmoji = '<:economy:701335275896307742>'
#     jEmoji = '<:business:701335275669946431>'
#     fEmoji = '<:first:701335275938381824>'
#     lEmoji = '<:large:701335275690786817>'
#     hEmoji = '<:heavy:701335275799969833>'
#     await ctx.send(yEmoji + jEmoji + fEmoji + lEmoji + hEmoji)

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
    await ctx.send('Usage (Since Last Reset):```ml\nInfo: ' + str(infoC) + '\nCompare: ' + str(compareC) + '\nSearch: ' + str(searchC) + '\nSeeall: ' + str(seeallC) + '\nPrice: ' + str(bot.priceC) + '\nWebsite: ' + str(websiteC) + '\nSheet: ' + str(sheetC) + '\nAirport: ' + str(airportC) + '\nAirline: ' + str(airlineC) + '\nFleet: ' + str(fleetC) + '```')
    
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
    if paused == False:
        await ctx.send(botinfo + '\nJoin our bot support server: https://discord.gg/4tVQHtf')

paused = False
@bot.command()
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
        
@bot.command()
@commands.has_role(646148607636144131)
async def reload(ctx):
    for cog in list(bot.extensions):
        bot.reload_extension(cog)
    await ctx.send('All extensions reloaded')
    
@bot.command(aliases = ['pause'])
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
