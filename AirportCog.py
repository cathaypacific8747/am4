info = 'Airport Extension v1.3'

import discord
from discord.ext import commands, tasks
from copy import deepcopy
import mysql.connector
from io import StringIO
import math
import csv
import urllib3
import time
import ast
import os
from checks import *
import traceback

acdb = mysql.connector.connect(user='***REMOVED***',
                               passwd='***REMOVED***',
                               host='***REMOVED***',
                               database='***REMOVED***')

cursor = acdb.cursor(buffered = True)
airportC = routesC = stopC = 0

if 1: # just to make the entire section collapsible and readable
    yI = '<:economy:701335275896307742>'
    jI = '<:business:701335275669946431>'
    fI = '<:first:701335275938381824>'
    lI = '<:large:701335275690786817>'
    hI = '<:heavy:701335275799969833>'

    definitions = {
        730781911860904006: 50,
        730781925815615529: 100,
        730781935059599472: 250,
        730781947705688104: 1000,
        730781956064673863: float('inf'),
    }

    with open('data/ap-indexed-radians.csv', newline='', encoding='utf-8-sig') as f:
        global airports
        airports = list(csv.reader(f))

    with open('data/ac-indexed.csv', newline='', encoding='utf-8-sig') as f:
        global aircrafts
        aircrafts = list(csv.reader(f))

    def calcCargoConfig(lh, maxCap, fPerDay, reputation=1):
        CAP_l = float(maxCap) * int(fPerDay) * 0.7
        DEM_l = int(lh[0]) / reputation
        DEM_h = int(lh[1]) / reputation

        if CAP_l >= DEM_l:
            CFG_l = DEM_l
            # large load has to be distributed to the DEM_h
            CFG_h = (CAP_l - DEM_l) / 0.7
            if DEM_h >= CFG_h:
                PCT_l = int(CFG_l / CAP_l * 100)
                PCT_h = 100 - PCT_l
                return [PCT_l/100, PCT_h/100]
            else: # not enough heavy demand
                return [0.0, 0.0]
        else:
            return [1.0, 0.0]

    def calcFirstPrioritizedSeats(yjf, maxSeats, fPerDay, reputation=1):
        y = int(yjf[0]) / reputation / int(fPerDay)
        j = int(yjf[1]) / reputation / int(fPerDay)
        f = int(yjf[2]) / reputation / int(fPerDay)

        fS = int(maxSeats / 3) if (f*3 > maxSeats) else int(f)
        jS = int((maxSeats - (fS*3)) / 2) if ((j*2 + f*3) > maxSeats) else int(j)
        yS = maxSeats - fS*3 - jS*2

        if yS < y:
            return [yS, jS, fS]
        else:
            return [0, 0, 0]

    def distanceCoor(lat1, lon1, lat2, lon2): # radians
        return 12742 * math.asin(math.sqrt(math.pow(math.sin((lat2-lat1) / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin((lon2-lon1) / 2), 2)))

    def findStopover1(oName, dName, shortName, isRealism=False): # None = malformed input
        o, d, range, rwyReq = [], [], -1, 0 # in case if airport is not found

        ##  get aircraftRange and minRwy whenever possible  ##
        for ac in aircrafts:
            if ac[1] == shortName:
                range = int(ac[12])
                isCargo = bool(int(ac[19]))
                if isRealism:
                    rwyReq = int(ac[11]) # if easy, the rwy is unlimited as set by default.
                break

        ##  get input airport details  ##
        for ap in airports:
            # IATA
            if ap[3] == oName: o = ap
            if ap[3] == dName: d = ap
            # ICAO
            if ap[4] == oName: o = ap
            if ap[4] == dName: d = ap
            # expected to take more computing power, but allows different inputs;
            # i.e. LHR > YSSY returns values.

        if o != [] and d != [] and range != -1:
            # only if there aren't inputErrors:
            dist = distanceCoor(float(o[7]), float(o[8]), float(d[7]), float(d[8]))
            if dist < range and dist > 100:
                # no stopovers are needed, so just return o/d information
                stpvrCandidates = ['', '---', '---', '---', '----', '', '', '', '', 0, 0]
            else:
                # there aren't any errors, so filter out the most distance-efficient stopover
                stpvrCandidates = deepcopy(airports)
                for ap in stpvrCandidates:
                    try:
                        oD = distanceCoor(float(o[7]), float(o[8]), float(ap[7]), float(ap[8])) # origin > thisAirport distance
                        dD = distanceCoor(float(d[7]), float(d[8]), float(ap[7]), float(ap[8])) # destnt > thisAirport distance
                        
                        if oD < 100 or dD < 100: raise ValueError() # location is the hub/ below game lower distance limit
                        if oD > range or dD > range: raise ValueError() # aircraft's range too short
                        if rwyReq > int(ap[5]): raise ValueError() # aircraft's rwy too short

                        ap.extend([oD, dD])
                    except ValueError:
                        ap.extend([float('inf'), float('inf')]) # set both at max, such that it will be at the bottom

                stpvrCandidates.sort(key=lambda x:x[9]+x[10]) # sort by stopover airport with the lease o/d distance
                stpvrCandidates = stpvrCandidates[0]

            if stpvrCandidates[9] + stpvrCandidates[10] == float('inf'):
                return 'UNREACHABLE'
            else:
                stpvrCandidates.extend([o[0], o[1], o[2], d[0], d[1], d[2], range, dist])
                return stpvrCandidates
        else:
            return None

    def findStopoverRaw(o, d, range, isCargo, rwyReq):
        if o != [] and d != [] and range != -1:
            # only if there aren't inputErrors:
            dist = distanceCoor(float(o[7]), float(o[8]), float(d[7]), float(d[8]))
            if dist < range and dist > 100:
                # no stopovers are needed, so just return o/d information
                stpvrCandidates = ['', '---', '---', '---', '----', '', '', '', '', 0, 0]
            else:
                # there aren't any errors, so filter out the most distance-efficient stopover
                stpvrCandidates = deepcopy(airports)
                for ap in stpvrCandidates:
                    try:
                        oD = distanceCoor(float(o[7]), float(o[8]), float(ap[7]), float(ap[8])) # origin > thisAirport distance
                        dD = distanceCoor(float(d[7]), float(d[8]), float(ap[7]), float(ap[8])) # destnt > thisAirport distance
                        
                        if oD < 100 or dD < 100: raise ValueError() # location is the hub/ below game lower distance limit
                        if oD > range or dD > range: raise ValueError() # aircraft's range too short
                        if rwyReq > int(ap[5]): raise ValueError() # aircraft's rwy too short

                        ap.extend([oD, dD])
                    except ValueError:
                        ap.extend([float('inf'), float('inf')]) # set both at max, such that it will be at the bottom

                stpvrCandidates.sort(key=lambda x:x[9]+x[10]) # sort by stopover airport with the lease o/d distance
                stpvrCandidates = stpvrCandidates[0]

            if stpvrCandidates[9] + stpvrCandidates[10] == float('inf'):
                return 'UNREACHABLE'
            else:
                stpvrCandidates.extend([o[0], o[1], o[2], d[0], d[1], d[2], range, dist])
                return stpvrCandidates
        else:
            return None

    def tickets(distance, isRealism=False, isCargo=False):
        if isCargo:
            if isRealism:
                l = math.floor(((0.000776321822039374 * distance + 0.860567600367807000) - 0.01) * 1.10 * 100) / 100
                h = math.floor(((0.000517742799409248 * distance + 0.256369915396414000) - 0.01) * 1.08 * 100) / 100
            else:
                l = math.floor(((0.000948283724581252 * distance + 0.862045432642377000) - 0.01) * 1.10 * 100) / 100
                h = math.floor(((0.000689663577640275 * distance + 0.292981124272893000) - 0.01) * 1.08 * 100) / 100
            return [l, h]
        else:
            if isRealism:
                y = math.floor((0.3 * distance + 150) * 1.10 / 10) * 10
                j = math.floor((0.6 * distance + 500) * 1.08 / 10) * 10
                f = math.floor((0.9 * distance + 1000) * 1.06 / 10) * 10
            else:
                y = math.floor((0.4 * distance + 170) * 1.10 / 10) * 10
                j = math.floor((0.8 * distance + 560) * 1.08 / 10) * 10
                f = math.floor((1.2 * distance + 1200) * 1.06 / 10) * 10
            return [y, j, f]

    def returnEmbed(e, rts, o, needsStopover, range, isCargo, rwyReq, maxIncome, startIndex, showMax=3):
            rt = rts[startIndex:]
            endIndex = startIndex
            showedCount = 0
            for d in rt:
                try:
                    v = ''
                    if needsStopover:
                        dR = [d[0], d[4], d[5], '' , '', '', '', airports[int(d[0])-1][7], airports[int(d[0])-1][8]] # get the coordinates for processing the stopover
                        stpvr = findStopoverRaw(o, dR, range, isCargo, rwyReq)
                        if stpvr == 'UNREACHABLE' or stpvr == None:
                            raise ValueError('noStopovers')
                        else:
                            if stpvr[0] != '':
                                v += f'**Stopover**: {stpvr[1]}, {stpvr[2]}\n'
                                v += f'​     {stpvr[3]} | {stpvr[4]}\n'
                    if isCargo:
                        v += f'​**​  Demand**: {lI} `{1000*round(0.5*int(d[1])):<7.0f}​` {hI} `{1000*int(d[2]):<7.0f}​`\n'
                        v += f'​**​  Config**: {lI} `{d[11][0]:<7.0%}​` {hI} `{d[11][1]:<7.0%}​`\n'
                        v += f'​**     Tickets**: {lI} `{d[12][0]:<7.2f}​` {hI} `{d[12][1]:<7.2f}​`\n'
                    else:
                        v += f'​**​  Demand**: {yI} `{d[1]:<4}​` {jI} `{d[2]:<5}​` {fI} `{d[3]:<5}​`\n'
                        v += f'​**​  Config**: {yI} `{d[11][0]:<4.0f}​` {jI} `{d[11][1]:<5.0f}​` {fI} `{d[11][2]:<5.0f}​`\n'
                        v += f'​**     Tickets**: {yI} `{d[12][0]:<4.0f}​` {jI} `{d[12][1]:<5.0f}​` {fI} `{d[12][2]:<5.0f}​`\n'
                        # side note: it is impossible for y-class tickets to exceed ~ $8994, so padding is limited to 4 to conserve space.
                    if rwyReq > 0: # isRealism
                        v += f'​**   Runway**: {d[8]} *ft*\n'
                    v += f'** ​Distance**: {d[9]} *km*\n'
                    v += f'**​     Income**: $ {int(d[10]):,d}/ flight ({int(d[10])/int(maxIncome):.1%})\n'
                    
                    e.add_field(name=f'**{d[4]}**, {d[5]}\n{d[6]} | {d[7]}', value=v, inline=False)
                    showedCount += 1
                    if showedCount == showMax:
                        break
                except:
                    pass # don't add in the route if stopovers are not possible
                finally:
                    endIndex += 1
            if showedCount == 0:
                e.add_field(name='Information', value='Unfortunately, there are no profitable routes.')
            # e.add_field(name=discord.utils.escape_markdown('__________________________'), value="Support us by [donating](https://www.paypal.com) ˘◡˘")
            return [e, endIndex] # this will be stored for future reqeusts for 'next/prev page'

    def progress(now, max):
        filled = int(20*now/max) * '█'
        return f'{now/max:>6.1%} [{filled:<20}] {now}/{max}'

    def eta(nowTime, startTime, now, max):
        return f'ETA: {(max-now)*(nowTime-startTime)/now:.1f}s left'

class AirportCog(commands.Cog, name = 'Airport Commands'):
    def __init__(self, bot):
        self.bot = bot
        print('Loaded ' + info + '!')

    '''
    Public use:
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    $airport
    $stop|route
    $routes
    '''

    @commands.command(help='Shows info of a selected airport.', usage='$airport <IATA or ICAO code of selected airport>', enabled = True)
    @notDM()
    @notPriceAlert()
    async def airport(self, ctx, code):
        global airportC
        airportC += 1
        succ = False
        nsucc = False
        name = ''
        injection = False
        if code[0] == "'":
            injection = True
        if injection == False:
            #try:
                #acdb.reconnect(attempts = 5, delay = 0.5)
                #cursor.execute(f"SELECT `Name` FROM `airports` WHERE `ICAO` = '{code}' OR `IATA` = '{code}'")
                #acdb.close()
            #except mysql.connector.Error as error:
                #await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')
            #for ap in cursor:
                #nsucc = True
                #name = ap[0]
            try:
                acdb.reconnect(attempts = 5, delay = 0.5)
                cursor.execute(f"SELECT `id`, ` arpt`, ` rgn`, ` iata`, ` icao`, ` rwy`, ` mrkt` FROM `arpt` WHERE ` ICAO` = '{code}' OR ` IATA` = '{code}'")
                acdb.close()
            except mysql.connector.Error as error:
                await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')
            for ap in cursor:
                succ = True
                if nsucc == False:
                    name = ap[1] + " Airport"
                await ctx.send(f'**{name.encode("iso-8859-1", "replace").decode("utf8", "replace")}** Stats```python\n         City: {ap[1]}, {ap[2]}'
                               f'\n         IATA: {ap[3]}\n         ICAO: {ap[4]}\nRunway Length: {int(ap[5]):,} ft.\n Market Value: {ap[6]}%\n```')    
            if succ == False:
                await ctx.send('Airport not found. You may have misspelled its IATA/ICAO or it isn\'t in the game.')

    @commands.command(aliases=['route'], brief='Shows the details and/or stopover of a route.', help='Shows the details of the any given route, including the best stopover whenever possible, configuration and ticket prices.\nThe field(s) [flights per day] and [reputation] is optional.', usage='$stop|route <Origin IATA/ICAO code> <Destination IATA/ICAO code> <aircraft code> [optional: flights per day] [optional: reputation]')
    @notDM()
    @notPriceAlert()
    async def stop(self, ctx, oName, dName, shortACname, *args):
        global stopC
        stopC += 1 #this is just a counter, don't worry about it

        success = False
        if len(args) == 0:
            success = True
            flightsPerDay, reputation = 0, 87
        elif len(args) == 1:
            if isPositiveInteger(args[0]):
                success = True
                flightsPerDay, reputation = int(args[0]), 87
            else:
                await ctx.send('Flights per day must be a positive integer or left blank. Please see proper command usage with `$help route`.')
        elif len(args) == 2:
            if isPositiveInteger(args[0]):
                if isPositiveInteger(args[1]):
                    flightsPerDay, reputation = int(args[0]), int(args[1])
                    success = True
                else:
                    await ctx.send('Reputation must be an positive integer or left blank. Please see proper command usage with `$help route`.')
            else:
                await ctx.send('Flights per day must be a positive integer or left blank. Please see proper command usage with `$help route`.')
        else:
            await ctx.send('Too many arguments. Please see proper command usage with `$help route`.')

        if success:
            # valid inputs, so continue.
            capacityMod = 1.06 if '+' in shortACname else 1
            shortACname = shortACname.replace('+', '').lower()
            reputation = int(reputation)

            # find the aircraft, determine its capacity and whether is cargo.
            for ac in aircrafts:
                if ac[1] == str(shortACname):
                    isCargo = bool(int(ac[19]))
                    capacity = int(ac[10]) * capacityMod if isCargo else int(ac[10])
                    flightsPerDay = int(flightsPerDay)
                    break
            
            if 'capacity' not in locals():
                await ctx.send('Aircraft not found. See `$help` for proper command usage.')
            else:
                # determine whether if the user's Easy/Realism.
                try:
                    isRealism = discord.utils.get(ctx.guild.roles, name='Realism') in ctx.author.roles # checks whether the user is Realism or not
                except:
                    isRealism = False

                # find stopover, returns an 'error', 'unreachable'
                stpvr = findStopover1(oName.upper(), dName.upper(), shortACname.lower(), isRealism)

                if stpvr == None:
                    msg = '‎\u200B\n'
                    msg += 'Airport(s) not found. See `$help` for proper command usage.'
                    await ctx.send(msg)
                elif stpvr == 'UNREACHABLE':
                    msg = '‎\u200B\n'
                    msg += f'There are **no possible stopovers** for this route. Choose another route.'
                    await ctx.send(msg)
                else:
                    embedColor = 0x277ecd if isRealism else 0x1a7939
                    ttl =  f'__**{stpvr[12]}**__, {stpvr[13]}'
                    ttl += f' <:to:704927870438342697> '
                    ttl += f'__**{stpvr[15]}**__, {stpvr[16]}'
                    if flightsPerDay:
                        ttl += f' @ {reputation}% reputation'
                    embed = discord.Embed(
                        title=ttl,
                        colour=embedColor
                    )

                    rt =  f'**Distance**: {int(stpvr[18])} *km*\n'
                    # WARNING: Some of the following spaces, which are used to align non-monospace text are NOT regular, 0.25em spaces, 
                    # rather spaces with specific widths, retreived from: http://jkorpela.fi/chars/spaces.html.

                    success = False
                    # Get the demand of that route from the combinations database.
                    # When flightPerDay is supplied, also determine its best configuration.
                    with open(f'data/dist/{stpvr[11]}.csv', 'r', newline='', encoding='utf-8-sig') as f:
                        dests = list(csv.reader(f))
                        for dest in dests:
                            if dest[0] == stpvr[14]:
                                if isCargo:
                                    lD, hD = round(1000 * round(int(dest[1])*0.5)), round(1000 * int(dest[2]))
                                    rt += f'** Demand**: {lI} `{lD:<7}​` {hI} `{hD:<7}​`\n'
                                    if flightsPerDay > 0:
                                        cfg = calcCargoConfig([lD, hD], capacity, flightsPerDay, reputation/100)
                                        print(cfg, capacity, flightsPerDay)
                                        rt += f'**  Config**: {lI} `{cfg[0]:<7.0%}​` {hI} `{cfg[1]:<7.0%}​`\n'
                                        if cfg[0] or cfg[1]:
                                            success = True
                                            t = tickets(int(stpvr[18]), isRealism, True)
                                            rt += f'**  Tickets**: {lI} `{t[0]:<7}​` {hI} `{t[1]:<7}​`\n'
                                            rt += f'**  Income**: ${int(reputation/100*(t[0]*cfg[0]*capacity*0.7 + t[1]*cfg[1]*capacity)):,d}/ flight'
                                    else:
                                        success = True
                                else: # pax
                                    yD, jD, fD = dest[1], dest[2], dest[3]
                                    rt += f'** Demand**: {yI} `{yD:<5}​` {jI} `{jD:<5}​` {fI} `{fD:<5}​`\n'
                                    if flightsPerDay > 0:
                                        cfg = calcFirstPrioritizedSeats([yD, jD, fD], capacity, flightsPerDay, reputation/100)
                                        rt += f'**  Config**: {yI} `{cfg[0]:<5}​` {jI} `{cfg[1]:<5}​` {fI} `{cfg[2]:<5}​`\n'
                                        if cfg[0] or cfg[1] or cfg[2]:
                                            success = True
                                            t = tickets(int(stpvr[18]), isRealism, False)
                                            rt += f'**  Tickets**: {yI} `{t[0]:<5}​` {jI} `{t[1]:<5}​` {fI} `{t[2]:<5}​`\n'
                                            rt += f'**  Income**: ${int(reputation/100*(t[0]*cfg[0] + t[1]*cfg[1] + t[2]*cfg[2])):,d}/ flight'
                                    else:
                                        success = True
                                break
                    
                    if success:
                        embed.add_field(name='__Route Information__', value=rt, inline=False)

                        if stpvr[0] != '':
                            s =  f'**   IATA**: {stpvr[3]}\n'
                            s += f'**   ICAO**: {stpvr[4]}\n'
                            s += f'**Location**: {stpvr[1]},\n'
                            s += f'     {stpvr[2]}\n'
                            s += f'**       Diff**: {stpvr[9]+stpvr[10]-stpvr[18]:+.5f} *km*\n'
                            if isRealism: s += f'** Runway**: {stpvr[5]} *ft*'
                            embed.add_field(name='__Stopover Information__', value=s, inline=False)

                        embed.set_footer(text='Database and formulae provided by Scuderia Airlines and Cathay Express.\nSupport us by donating! For more info, use the $donate command.')
                        await ctx.send(embed=embed)
                    else:
                        msg = '‎\u200B\n'
                        msg += f'With `{flightsPerDay}` flights per day, this route does not have enough demand to be profitable.\n'
                        msg += f'Consider reducing the number of flights per day.'
                        await ctx.send(msg)

    @commands.command(brief='Finds the most profitable routes.', help='Shows the most profitable routes given the maximum distance and origin airport.\nFor training-points-enhanced cargo load (1.06x capacity), add a "+" at the back of the <aircraft code>.', usage='$routes <Origin IATA/ICAO code> <aircraft code> <target distance> <flights per day> [optional: reputation]')
    @notDM()
    @notPriceAlert()
    async def routes(self, ctx, airportName, shortACname, targetDistance, flightsPerDay, *reputation):
        if len(reputation) == 0: reputation = [87]
        
        global routesC
        routesC += 1 #this is just a counter, don't worry about it
        
        if not isPositiveInteger(targetDistance):
            await ctx.send('Target distance must be a positive integer. Please see proper command usage with `$help routes`.')
        elif not isPositiveInteger(flightsPerDay):
            await ctx.send('Flights per day must be a positive integer. Please see proper command usage with `$help routes`.')
        elif len(reputation) > 1:
            await ctx.send('Too many arguments. Please see proper command usage with `$help routes`.')
        elif not isPositiveInteger(reputation[0]):
            await ctx.send('Reputation must be a positive integer or left blank. Please see proper command usage with `$help routes`.')
        else:
            # valid inputs, so continue.
            reputation = int(reputation[0])
            capacityMod = 1.06 if '+' in shortACname else 1
            shortACname = shortACname.replace('+', '').lower()
            airportName = airportName.upper()

            try:
                isRealism = discord.utils.get(ctx.guild.roles, name='Realism') in ctx.author.roles # checks whether the user is Realism or not
            except:
                isRealism = False

            o, range, rwyReq, needsStopover = [], -1, 0, False # in case if airport is not found
            ##  get aircraftRange and minRwy whenever possible  ##
            for ac in aircrafts:
                if ac[1] == shortACname:
                    fullName = ac[3] if ac[2] == 'Other' else f'{ac[2]} {ac[3]}' # e.g. NOT('Other MC-21-400') > 'MC-21-400'
                    isCargo = bool(int(ac[19]))
                    range = int(ac[12])
                    capacity = int(ac[10]) * capacityMod if isCargo else int(ac[10])
                    if isRealism: rwyReq = int(ac[11]) # if easy, the rwy is unlimited as set by default.
                    break

            for ap in airports:
                if ap[3] == airportName or ap[4] == airportName: 
                    o = ap # iata/icao recognisation
                    break

            if o == [] or range == -1:
                await ctx.send('Airport and/or aircraft not found. See $help for proper command usage.')
            else:
                if int(targetDistance) > range * 2:
                    msg = f':warning:**Warning: **Target Distance ({targetDistance} km) is larger than the maximum stopover range of the aircraft ({range*2} km).\n'
                    msg += f'Now assuming your target distance to be **{range*2}** km.'
                    await ctx.send(msg)
                    targetDistance = range * 2
                if int(targetDistance) > 20015:
                    msg = f':warning:**Warning: **Target Distance ({targetDistance} km) is larger than half of the circumference of Earth.\n'
                    msg += f'Now assuming your target distance to be **20015** km.'
                    await ctx.send(msg)
                    targetDistance = 20015
                if int(targetDistance) > range or int(targetDistance) < 100:
                    # stopovers are needed, so set the flag
                    needsStopover = True

                with open(f'data/dist/{o[0]}.csv', newline='', encoding='utf-8-sig') as f:
                    data, filtered = list(csv.reader(f)), []

                    for d in data:
                        if int(d[9]) <= int(targetDistance) and int(d[8]) >= rwyReq:
                            filtered.append(d)

                    # storage structure: List {
                    #   0: destId
                    #   1: yDemand
                    #   2: jDemand
                    #   3: fDemand
                    #   4: destCity
                    #   5: destRegion
                    #   6: destIATA
                    #   7: destICAO
                    #   8: runwayLength
                    #   9: directDistance
                    #   10: configuration[y,j,f]/[l,h]
                    #   11: ticket prices[y,j,f]/[l,h]
                    # }

                    for f in filtered:
                        try:
                            if isCargo:
                                cargoCfg = calcCargoConfig([round(int(f[1])*500, -3), round(int(f[2])*1000, -3)], int(capacity), int(flightsPerDay), int(reputation)/100) # configuration in decimal percentages
                                ticketP = tickets(int(f[9]), isRealism, True) # cargo prices
                                thisIncome = int(int(reputation)/100*(ticketP[0] * (cargoCfg[0]*capacity*0.7) + ticketP[1] * (cargoCfg[1]*capacity)))
                                f.extend([thisIncome, cargoCfg, ticketP])
                            else:
                                paxCfg = calcFirstPrioritizedSeats([int(f[1]), int(f[2]), int(f[3])], capacity, int(flightsPerDay), int(reputation)/100) # pax in pure seats
                                ticketP = tickets(int(f[9]), isRealism, False) # pax prices
                                thisIncome = int(int(reputation)/100*(ticketP[0]*paxCfg[0] + ticketP[1]*paxCfg[1] + ticketP[2]*paxCfg[2]))
                                f.extend([thisIncome, paxCfg, ticketP])
                        except:
                            f.extend([0, [0, 0, 0], [0, 0, 0]])
                    
                    # calculate the maximum achieveable demand given infinite demand and maximum distance
                    maxIncome = tickets(int(targetDistance), isRealism, True)[0]*capacity*0.7 if isCargo else tickets(int(targetDistance), isRealism, False)[0]*capacity
                    
                    filtered.sort(key=lambda x:x[10], reverse=True) # best first, worst last
                    storage = [i for i in filtered if i[10] > 0] # for which income is profitable.

                    e = discord.Embed(
                        title=f'{fullName} <:departing:708937853157245010> __**{o[1]}**__, {o[2]} @ {reputation:.0f}% reputation',
                        colour=0x277ecd if isRealism else 0x1a7939
                    )
                    e = returnEmbed(e, storage, o, needsStopover, range, isCargo, rwyReq, maxIncome, 0)
                    e[0].set_footer(text=f'Database and formulae provided by Scuderia Airlines and Cathay Express.')
                    display = await ctx.send(embed=e[0])

                    # upload all combinations to Discord, by using StringIO.
                    stringIOstorage = StringIO(str(storage).replace(', ', ','))
                    storageInstance = await self.bot.get_channel(703962961592713267).send(file=discord.File(stringIOstorage, filename='routesStorage.txt'))

                    # then retrieve the storageMessageId and include it for further use
                    oldEmbed = display.embeds[0]
                    oldEmbed.set_footer(text=f'Database and formulae provided by Scuderia Airlines and Cathay Express.\nSupport us by donating! For more info, use the $donate command.\nMessage Id: {storageInstance.id}​{o[0]}​{int(needsStopover)}​{range}​{int(isCargo)}​{rwyReq}​0​{e[1]}​{int(maxIncome)}')
                    await display.edit(embed=oldEmbed)

                    # then check whether there are more routes to show.
                    await display.add_reaction('<:download_as_csv:730233914412498974>')
                    if e[1] < len(storage):
                        await display.add_reaction('<:next_page:705723955020955708>')

        # delete variables to conserve RAM
        capacityMod = isRealism = o = range = rwyReq = needsStopover = ac = fullName = isCargo = capacity = ap = f = data = filtered = d = ticketP = thisIncome = maxIncome = storage = e = display = stringIOstorage = storageInstance = oldEmbed = cargoCfg = paxCfg = None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id:
            reactor = await self.bot.fetch_user(payload.user_id)
            if payload.emoji.id in [705724371452428309, 705723955020955708]:
                msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await msg.clear_reactions()

                oldEmbed = msg.embeds[0]
                oldEmbedData = oldEmbed.footer.text.split(': ')[1].split('​')
                
                data = await self.bot.get_channel(703962961592713267).fetch_message(int(oldEmbedData[0]))
                combinations = ast.literal_eval(urllib3.PoolManager().request('GET', data.attachments[0].url).data.decode('utf-8')) # this isn't dangerous at all. No user input is involved.
                
                o = airports[int(oldEmbedData[1])-1]
                needsStopover, range, isCargo, rwyReq, maxIncome = bool(int(oldEmbedData[2])), int(oldEmbedData[3]), bool(int(oldEmbedData[4])), int(oldEmbedData[5]), int(oldEmbedData[8])
                startIndex = max(0, int(oldEmbedData[6])-3) if payload.emoji.id == 705724371452428309 else int(oldEmbedData[7])

                e = discord.Embed(title=oldEmbed.title, colour=oldEmbed.colour)
                e = returnEmbed(e, combinations, o, needsStopover, range, isCargo, rwyReq, maxIncome, startIndex)
                e[0].set_footer(text=f'Database and formulae provided by Scuderia Airlines and Cathay Express.\nSupport us by donating! For more info, use the $donate command.\nMessage Id: {oldEmbedData[0]}​{o[0]}​{int(needsStopover)}​{range}​{int(isCargo)}​{rwyReq}​{startIndex}​{e[1]}​{maxIncome}')

                await msg.edit(embed=e[0])
                await msg.add_reaction('<:download_as_csv:730233914412498974>')
                if startIndex:
                    await msg.add_reaction('<:previous_page:705724371452428309>')
                if e[1] < len(combinations): # if there are more routes to __possibly__ show
                    await msg.add_reaction('<:next_page:705723955020955708>')
            elif payload.emoji.id == 730233914412498974:
                try:
                    v =  'Please select the *maximum* amount of routes to be downloaded.\n'
                    v += '> <:50_results:730781911860904006> - 50 results\n'
                    v += '> <:100_results:730781925815615529> - 100 results\n'
                    v += '> <:250_results:730781935059599472> - 250 results\n'
                    v += '> <:1000_results:730781947705688104> - 1000 results\n'
                    v += '> <:all_results:730781956064673863> - All results (not recommended)\n'
                    v += '*CSV generation times and processing power are dependent on the number of results chosen.*\n'
                    v += f'||Reference Id: {payload.channel_id}>{payload.message_id}||'
                    ask = await reactor.send(v)
                    await ask.add_reaction('<:50_results:730781911860904006>')
                    await ask.add_reaction('<:100_results:730781925815615529>')
                    await ask.add_reaction('<:250_results:730781935059599472>')
                    await ask.add_reaction('<:1000_results:730781947705688104>')
                    await ask.add_reaction('<:all_results:730781956064673863>')
                except Exception:
                    await self.bot.get_channel(id=475629813831565312).send(traceback.format_exc())
                    await self.bot.get_channel(payload.channel_id).send(f'<@{payload.user_id}> I was not able to send you a confirmation message by a DM. Please check your privacy settings or unlock me.')
            elif payload.emoji.id in [730781911860904006,730781925815615529,730781935059599472,730781947705688104,730781956064673863]:
                try:
                    maxRoutes = definitions[payload.emoji.id]
                    
                    ask = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

                    origMessage = ask.content.split('||')[1].split(': ')[1].split('>')
                    loadingMessage = await reactor.send('Initialising...')
                    await ask.delete()

                    msg = await self.bot.get_channel(int(origMessage[0])).fetch_message(int(origMessage[1]))
                    oldEmbed = msg.embeds[0]
                    oldEmbedData = oldEmbed.footer.text.split(': ')[1].split('​')
                    
                    await loadingMessage.edit(content='Downloading data...')
                    data = await self.bot.get_channel(703962961592713267).fetch_message(int(oldEmbedData[0]))
                    combinations = ast.literal_eval(urllib3.PoolManager().request('GET', data.attachments[0].url).data.decode('utf-8')) # this isn't dangerous at all. No user input is involved.
                    
                    o = airports[int(oldEmbedData[1])-1]
                    needsStopover, range, isCargo, rwyReq, maxIncome = bool(int(oldEmbedData[2])), int(oldEmbedData[3]), bool(int(oldEmbedData[4])), int(oldEmbedData[5]), int(oldEmbedData[8])
                    
                    counter, successCounter = 0, 0
                    # define the headers of the csv.
                    if isCargo:
                        entries = [['Stop IATA', 'Stop ICAO', 'Stop Name', 'Stop Country', '',
                                    'Dest IATA', 'Dest ICAO', 'Dest Name', 'Dest Country', '',
                                    'Distance', 'Runway', 'Income', 'Profitability', '',
                                    'Large Demand', 'Heavy Demand', '',
                                    'Large Config', 'Heavy Config', '',
                                    'Large Tickets', 'Heavy Tickets']]
                    else:
                        entries = [['Stop IATA', 'Stop ICAO', 'Stop Name', 'Stop Country', '',
                                    'Dest IATA', 'Dest ICAO', 'Dest Name', 'Dest Country', '',
                                    'Distance', 'Runway', 'Income', 'Profitability', '',
                                    'Economy Demand', 'Business Demand', 'First Demand', '',
                                    'Economy Config', 'Business Config', 'First Config', '',
                                    'Economy Tickets', 'Business Tickets', 'First Tickets']]
                    
                    maxRoutesDisplay = len(combinations) if maxRoutes == float('inf') else maxRoutes
                    startTime = lastLoggedTime = time.time()
                    numOfDots = 1
                    for d in combinations:
                        try:
                            thisEntry = []
                            # GROUP 1: Stopovers (whenver applicable)
                            stpvrInfo = ['---', '---', '---', '---', '']
                            if needsStopover:
                                dR = [d[0], d[4], d[5], '' , '', '', '', airports[int(d[0])-1][7], airports[int(d[0])-1][8]] # get the coordinates for processing the stopover
                                stpvr = findStopoverRaw(o, dR, range, isCargo, rwyReq)
                                if stpvr == 'UNREACHABLE' or not stpvr:
                                    raise ValueError('noStopovers')
                                else:
                                    if stpvr[0]:
                                        stpvrInfo = [stpvr[3], stpvr[4], stpvr[1], stpvr[2], '']
                            thisEntry.extend(stpvrInfo)
                            
                            # GROUP 2: Destination
                            thisEntry.extend([d[6], d[7], d[4], d[5], ''])

                            # GROUP 3: General Information
                            thisEntry.extend([d[9], d[8], int(d[10]), f'{int(d[10])/int(maxIncome):.2%}', ''])

                            # GROUP 4: Demands, Configs and Tickets
                            if isCargo:
                                thisEntry.extend([f'{1000*round(0.5*int(d[1])):.0f}', f'{1000*int(d[2]):.0f}', ''])
                                thisEntry.extend([f'{d[11][0]:.0%}', f'{d[11][1]:.0%}​', ''])
                                thisEntry.extend([f'{d[12][0]:.2f}​', f'{d[12][1]:.2f}', ''])
                            else:
                                thisEntry.extend([d[1], d[2], d[3], ''])
                                thisEntry.extend([f'{d[11][0]:.0f}', f'{d[11][1]:.0f}', f'{d[11][2]:.0f}', ''])
                                thisEntry.extend([f'{d[12][0]:.0f}', f'{d[12][1]:.0f}', f'{d[12][2]:.0f}', ''])
                            
                            entries.append(thisEntry)
                            successCounter += 1
                        except:
                            pass
                        finally:
                            counter += 1 # regardless of successState, increment it.
                            nowTime = time.time()
                            if nowTime-lastLoggedTime >= 1: # for every 1s intervals
                                if numOfDots > 3: numOfDots = 1
                                await loadingMessage.edit(content=f"Processing data{numOfDots*'.'} \n`{progress(counter, maxRoutesDisplay)}` {eta(nowTime, startTime, counter, maxRoutesDisplay)}")
                                lastLoggedTime = nowTime
                                numOfDots += 1

                        if successCounter >= maxRoutes:
                            break # stop attempting routes.
                    
                    # once outside the loop or done looping through all of them, create the CSV.
                    await loadingMessage.edit(content='Preparing CSV file...')
                    with open('output.csv', 'w+', newline='', encoding='utf-8-sig') as f:
                        csv.writer(f).writerows(entries) # did not use StringIO because BOM is required to open CSV as UTF-8 in Excel.
                    await loadingMessage.delete()
                    await reactor.send(file=discord.File('output.csv'))
                    os.remove('output.csv')
                except:
                    await reactor.send('Whoops! Something went wrong during the CSV generation. Please contact <@668261593502580787> with the original command.')
                    botmod = self.bot.get_channel(475629813831565312)
                    await botmod.send(f'<@{payload.user.id}> was unable to generate their CSV. \n<@&701415081547923516>')
                finally:
                    # delete variables to conserve RAM.
                    msg = oldEmbed = oldEmbedData = data = combinations = o = needsStopover = range = isCargo = rwyReq = maxIncome = ask = maxRoutes = origMessage = loadingMessage = counter = successCounter = entries = maxRoutesDisplay = startTime = lastLoggedTime = numOfDots = d = thisEntry = stpvrInfo = dR = stpvr = nowTime = f = None

def setup(bot):
    bot.add_cog(AirportCog(bot))