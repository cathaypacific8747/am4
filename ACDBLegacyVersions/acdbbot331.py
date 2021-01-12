V = 'v3.3.1'
botinfo = (f'**AM4 ACDB bot** {V}\n'
           f'made by **favorit1**\n'
           f'database and profit formula by **Scuderia Airlines**')


import discord
from discord.ext import commands, tasks

import mysql.connector

bot = commands.Bot(command_prefix = '$')

acdb = mysql.connector.connect(user='***REMOVED***',
                               passwd='***REMOVED***',
                               host='***REMOVED***',
                               database='***REMOVED***')

cursor = acdb.cursor(buffered = True)

from sys import executable, argv
from os import execl, path
def restart_program():
    execl(executable, path.abspath(__file__), * argv)

from random import randint
from time import gmtime, time, strftime
import json
from urllib.request import urlopen
from urllib.parse import quote

infoC = 0
compareC = 0
searchC = 0
seeallC = 0
priceC = 0
websiteC = 0
sheetC = 0
airportC = 0
fleetC = 0
airlineC = 0
def counter(cmd):
    global infoC, compareC, searchC, seeallC, priceC, websiteC, sheetC, airportC, fleetC, airlineC
    if cmd == 'info':
        infoC += 1
    elif cmd == 'compare':
        compareC += 1
    elif cmd == 'search':
        searchC += 1
    elif cmd == 'seeall':
        seeallC += 1
    elif cmd == 'price':
        priceC += 1
    elif cmd == 'website':
        websiteC += 1
    elif cmd == 'sheet':
        sheetC += 1
    elif cmd == 'airport':
        airportC += 1
    elif cmd == 'fleet':
        fleetC += 1
    elif cmd == 'airline':
        airlineC += 1
        
        
@bot.event
async def on_ready():
    if gmtime()[7] >= 311:
        acotd = randint(1, 310)
    else:
        acotd = gmtime()[7]
    num = 0
    cursor.execute(f'SELECT `aircraft` FROM `am4bot`')
    for ac in cursor:
        if num == acotd:
            await bot.change_presence(activity = discord.Activity(type = 3, name = f'AC of the day: {ac[0]}'))
        num += 1
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
    else:
        print(error)

@bot.command(aliases = ['tools', 'web'], help = 'Links to Scuderia\'s AM4 Tools Website')
async def website(ctx):
    if not paused:
        counter('website')
        await ctx.send(f'Here\'s the link to the AM4 Tools Website, created by Scuderia Airlines:\nhttps://scuderiaairlines.github.io/AM4-Guides-and-Tools/index.html')

@bot.command(aliases = ['excel', 'sheet'], help = 'Links to the AM4 AC Spreadsheet')
async def spreadsheet(ctx):
    if paused == False:
        counter('sheet')
        await ctx.send(f'Here\'s the link to the AM4 AC spreadsheet, created by Scuderia Airlines, and the rest of the Guide Development team:\nhttps://docs.google.com/spreadsheets/d/1YInKDK8fHmetOO1n9ZSyn8--gZhNmsY6BIjBoEhInTQ/edit?usp=sharing')
    
@bot.command(aliases = ['all', 'allac'], help = 'Links to a spreadsheet containing all short names of ACs to be used with the $info command', brief = 'Sends all short names of ACs')
async def seeall(ctx):
    if paused == False:
        counter('seeall')
        await ctx.send(f'Here\'s the link to all AC short names. These are to be used in almost all commands.\nhttps://docs.google.com/spreadsheets/d/1KfMM5N52mIIii_cwRFcHsjbo491DkTanBlC7piFofWk/edit?usp=sharing')

def profit(ac):
    tpriceE = round(((0.4 * ac[2]) + 170) * 1.10)
    tpriceR = round(((0.3 * ac[2]) + 150) * 1.10)
    co2 = float(ac[3]) * ac[6] * ac[2] * 0.13
    fuel = float(ac[4]) * ac[2] * 0.85
    fpdE = 24 / (ac[2] / (ac[5] * 1.5))
    fpdR = 24 / (ac[2] / ac[5])
    
    ppfE = round((tpriceE * ac[6]) - co2 - fuel)
    ppfR = round((tpriceR * ac[6]) - co2 - fuel)

    ppdE = round(ppfE * fpdE)
    ppdR = round(ppfR * fpdR)

    return (ppfR, fpdR, ppdR, ppfE, fpdE, ppdE)

def procargo(ac):
    tpriceE = round((((0.000948283724581252 * ac[2]) + 0.862045432642377000) - 0.01) * 1.10, 2)
    tpriceR = round((((0.000776321822039374 * ac[2]) + 0.860567600367807000) - 0.01) * 1.10, 2)
    co2 = ((ac[2] * ((ac[6] * 0.7)/1000) * float(ac[3])) + (0.95 * ac[6] * 0.7)) * 0.13
    fuel = float(ac[4]) * ac[2] * 0.85
    fpdE = 24 / (ac[2] / (ac[5] * 1.5))
    fpdR = 24 / (ac[2] / ac[5])
    
    ppfE = round((tpriceE * ac[6]) - co2 - fuel)
    ppfR = round((tpriceR * ac[6]) - co2 - fuel)

    ppdE = round(ppfE * fpdE)
    ppdR = round(ppfR * fpdR)
    
    return (ppfR, fpdR, ppdR, ppfE, fpdE, ppdE)
    

@bot.event
async def on_reaction_add(reaction, user):
    global msg, ac, pro, embed, ps, cs, rs, ss, fs, es, fr, dr, pr, fe, de, pe, ac1, ac2, pro1, pro2
    if user != reaction.message.author and str(reaction.emoji) == '📱':
        if ac[10] == 'Cargo':
            msg = (f'```ml\nPrice:\n"{ac[8]} million"\nCapacity:\n"{ac[6]:,} lbs"\nRange:\n"{ac[2]} km"\nSpeed:\n"{ac[5]} km/h"\nFuel consumption:\n"{ac[4]} lbs/km"\nCO2 emmisions:\n"{ac[3]} kg/1k lbs/km"\n'
               f'Profit per Flight (\'Realism\'):\n"${pro[0]:,}"\nFlights per day (\'Realism\'):\n"{round(pro[1], 2)}"\nProfit per Day (\'Realism\'):\n"${pro[2]:,}"\n'
               f'Profit per Flight (\'Easy\'):\n"${pro[3]:,}"\nFlights per day (\'Easy\'):\n"{round(pro[4], 2)}"\nProfit per Day (\'Easy\'):\n"${pro[5]:,}"```')
        else:
            msg = (f'```ml\nPrice:\n"{ac[8]} million"\nCapacity:\n"{ac[6]} pax"\nRange:\n"{ac[2]} km"\nSpeed:\n"{ac[5]} km/h"\nFuel consumption:\n"{ac[4]} lbs/km"\nCO2 emmisions:\n"{ac[3]} kg/pax/km"\n'
               f'Profit per Flight (\'Realism\'):\n"${pro[0]:,}"\nFlights per day (\'Realism\'):\n"{round(pro[1], 2)}"\nProfit per Day (\'Realism\'):\n"${pro[2]:,}"\n'
               f'Profit per Flight (\'Easy\'):\n"${pro[3]:,}"\nFlights per day (\'Easy\'):\n"{round(pro[4], 2)}"\nProfit per Day (\'Easy\'):\n"${pro[5]:,}"```')
        embed.set_field_at(0, name = 'Brief Statistics (Mobile)', value = msg)
        await reaction.message.edit(embed = embed)
    elif user != reaction.message.author and str(reaction.emoji) == '🦵':
        await reaction.message.edit(content = msg, suppress = True)
    elif user != reaction.message.author and str(reaction.emoji) == '🇲':
        ps = cs = rs = ss = fs = es = fr = dr = pr = fe = de = pe = '\n'
        if ac1[10] == 'Cargo':
            msg = (f'```ml\nPrice:{ps} "${ac1[8]} M" | "${ac2[8]} M"\nCapacity:{cs} "{ac1[6]:,} lbs" | "{ac2[6]:,} lbs"\n'
                   f'Range:{rs} "{ac1[2]} km" | "{ac2[2]} km"\nSpeed:{ss} "{ac1[5]} km/h" | "{ac2[5]} km/h"\n'
                   f'Fuel Consumption:{fs} "{ac1[4]} lbs/km" | "{ac2[4]} lbs/km"\nCO2 Emmisions:{es} "{ac1[3]} kg/k/km" | "{ac2[3]} kg/k/km"\n'
                   f'Profit per flight (\'Realism\'):{fr} "${pro1[0]:,}" | "${pro2[0]:,}"\nFlights per day (\'Realism\'):{dr} "{round(pro1[1], 2)}" | "{round(pro2[1], 2)}"\n'
                   f'Profit per day (\'Realism\'):{pr} "${pro1[2]:,}" | "${pro2[2]:,}"\nProfit per flight (\'Easy\'):{fe} "${pro1[3]:,}" | "${pro2[3]:,}"\n'
                   f'Flights per day (\'Easy\'):{de} "{round(pro1[4], 2)}" | "{round(pro2[4], 2)}"\nProfit per day (\'Easy\'):{pe} "${pro1[5]:,}" | "${pro2[5]:,}"```')
        else:
            msg = (f'```ml\nPrice:{ps} "${ac1[8]} M" | "${ac2[8]} M"\nCapacity:{cs} "{ac1[6]} pax" | "{ac2[6]} pax"\n'
                   f'Range:{rs} "{ac1[2]} km" | "{ac2[2]} km"\nSpeed:{ss} "{ac1[5]} km/h" | "{ac2[5]} km/h"\n'
                   f'Fuel Consumption:{fs} "{ac1[4]} lbs/km" | "{ac2[4]} lbs/km"\nCO2 Emmisions:{es} "{ac1[3]} kg/p/km" | "{ac2[3]} kg/p/km"\n'
                   f'Profit per flight (\'Realism\'):{fr} "${pro1[0]:,}" | "${pro2[0]:,}"\nFlights per day (\'Realism\'):{dr} "{round(pro1[1], 2)}" | "{round(pro2[1], 2)}"\n'
                   f'Profit per day (\'Realism\'):{pr} "${pro1[2]:,}" | "${pro2[2]:,}"\nProfit per flight (\'Easy\'):{fe} "${pro1[3]:,}" | "${pro2[3]:,}"\n'
                   f'Flights per day (\'Easy\'):{de} "{round(pro1[4], 2)}" | "{round(pro2[4], 2)}"\nProfit per day (\'Easy\'):{pe} "${pro1[5]:,}" | "${pro2[5]:,}"```')
        embed.set_field_at(0, name = 'Comparison (Mobile)', value = msg)
        await reaction.message.edit(embed = embed)
        
        
ac = ac1 = ac2 = pro1 = pro2 = msg = pro = embed = ps = cs = rs = ss = fs = es = fr = dr = pr = fe = de = pe = ''
@bot.command(aliases = ['ac'], help = 'Sends stats of a selected AC. Usage: $info <short name of an AC>', brief = 'Sends stats of a selected AC')
async def info(ctx, plane):
    if paused == False:
        global ac, msg, pro, embed
        counter('info')
        succ = False
        injection = False
        if plane[0] == "'":
            injection = True
        if injection == False:
            try:
                acdb.reconnect(attempts = 5, delay = 0.5)
                cursor.execute(f"SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type` FROM `am4bot` WHERE `shortname` = '{plane}'")
                acdb.close()
            except mysql.connector.Error as error:
                await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')
        for ac1 in cursor:
            ac = ac1
            if ac[10] == "Cargo":
                pro = procargo(ac1)
                msg = (f'```ml\n           Price: "{ac[8]} million"\n        Capacity: "{ac[6]:,} lbs"\n           Range: "{ac[2]} km"\n           Speed: "{ac[5]} km/h"\nFuel consumption: "{ac[4]} lbs/km"\n   CO2 emmisions: "{ac[3]} kg/1k lbs/km"\n'
                       f'Profit per Flight (\'Realism\'): "${pro[0]:,}"\n  Flights per day (\'Realism\'): "{round(pro[1], 2)}"\n   Profit per Day (\'Realism\'): "${pro[2]:,}"\n'
                       f'   Profit per Flight (\'Easy\'): "${pro[3]:,}"\n     Flights per day (\'Easy\'): "{round(pro[4], 2)}"\n      Profit per Day (\'Easy\'): "${pro[5]:,}"```')
            else:
                pro = profit(ac1)
                msg = (f'```ml\n           Price: "{ac[8]} million"\n        Capacity: "{ac[6]} pax"\n           Range: "{ac[2]} km"\n           Speed: "{ac[5]} km/h"\nFuel consumption: "{ac[4]} lbs/km"\n   CO2 emmisions: "{ac[3]} kg/pax/km"\n'
                       f'Profit per Flight (\'Realism\'): "${pro[0]:,}"\n  Flights per day (\'Realism\'): "{round(pro[1], 2)}"\n   Profit per Day (\'Realism\'): "${pro[2]:,}"\n'
                       f'   Profit per Flight (\'Easy\'): "${pro[3]:,}"\n     Flights per day (\'Easy\'): "{round(pro[4], 2)}"\n      Profit per Day (\'Easy\'): "${pro[5]:,}"```')
            embed = discord.Embed(title=f"{ac[1]}", colour=discord.Colour(0xd0021b))

            embed.set_image(url=f"https://www.airline4.net/assets/img/aircraft/png/{ac[9]}.png")
            embed.set_footer(text="Data and Profit Formula provided by Scuderia Airlines' AC database.")

            embed.add_field(name = 'Brief Statistics', value = msg)
            
            message = await ctx.send(embed = embed)
            await message.add_reaction('📱')
            await message.add_reaction('🦵')

            succ = True
        if injection:
            await ctx.send('SQL Injection detected. Stop it. Bad.')
        elif succ == False:
            await ctx.send('Aircraft not found. You can see all AC abbreviations with the command $seeall')

def addspaces(prm, amt):
    out = ""
    prm = str(prm)
    tamt = amt - len(prm)
    for i in range(tamt):
            out += " "
    return out
        
@bot.command(help = 'Compares two selected AC stats back to back. Usage: $compare <AC1> <AC2>', brief = 'Compares two selected AC stats back to back')
async def compare(ctx, plane1, plane2):
    if paused == False:
        global msg, embed, ac1, ac2, pro1, pro2, ps, cs, rs, ss, fs, es, fr, dr, pr, fe, de, pe
        counter('compare')
        succ1 = False
        succ2 = False
        injection = False
        if plane1[0] == "'" or plane2[0] == "'":
            injection = True
        ac1 = ''
        ac2 = ''
        if injection == False:
            try:
                acdb.reconnect(attempts = 5, delay = 0.5)
                cursor.execute(f"SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type` FROM `am4bot` WHERE `shortname` = '{plane1}'")
            except mysql.connector.Error as error:
                await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')    
            for ac in cursor:
                ac1 = ac
                succ1 = True

            try:
                cursor.execute(f"SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type` FROM `am4bot` WHERE `shortname` = '{plane2}'")
                acdb.close()
            except mysql.connector.Error as error:
                await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')
            for ac in cursor:
                ac2 = ac
                succ2 = True
        
        if injection == True:
            await ctx.send('SQL Injection detected. Stop it. Bad.')
        elif succ1 == False and succ2 == False:
            await ctx.send('Neither of the aircraft found. You can see all AC abbreviations with the command $seeall')    
        elif succ1 == False:
            await ctx.send('First aircraft not found. You can see all AC abbreviations with the command $seeall')
        elif succ2 == False:
            await ctx.send('Second aircraft not found. You can see all AC abbreviations with the command $seeall')
        elif ac1[10] != ac2[10]:
            await ctx.send("Can't compare cargo and pax aircraft")
            ac1 = ac2 = None
        try:
            if ac1[10] == 'Cargo':
                pro1 = procargo(ac1)
                pro2 = procargo(ac2)
            else:
                pro1 = profit(ac1)
                pro2 = profit(ac2)
        except:
            pass
        ps = addspaces(ac1[8], 20)
        cs = addspaces(ac1[6], 16)
        rs = addspaces(ac1[2], 20)
        ss = addspaces(ac1[5], 18)
        fs = addspaces(ac1[4], 5)
        es = addspaces(ac1[3], 7)
        
        fr = addspaces(f'{pro1[0]:,}', 9)
        dr = addspaces(round(pro1[1], 2), 12)
        pr = addspaces(f'{pro1[2]:,}', 12)
        fe = addspaces(f'{pro1[3]:,}', 12)
        de = addspaces(round(pro1[4], 2), 15)
        pe = addspaces(f'{pro1[5]:,}', 15)

        if ac1[10] == 'Cargo':
            msg = (f'```ml\nPrice:{ps} "${ac1[8]} M" | "${ac2[8]} M"\nCapacity:{cs} "{ac1[6]:,} lbs" | "{ac2[6]:,} lbs"\n'
                   f'Range:{rs} "{ac1[2]} km" | "{ac2[2]} km"\nSpeed:{ss} "{ac1[5]} km/h" | "{ac2[5]} km/h"\n'
                   f'Fuel Consumption:{fs} "{ac1[4]} lbs/km" | "{ac2[4]} lbs/km"\nCO2 Emmisions:{es} "{ac1[3]} kg/k/km" | "{ac2[3]} kg/k/km"\n'
                   f'Profit per flight (\'Realism\'):{fr} "${pro1[0]:,}" | "${pro2[0]:,}"\nFlights per day (\'Realism\'):{dr} "{round(pro1[1], 2)}" | "{round(pro2[1], 2)}"\n'
                   f'Profit per day (\'Realism\'):{pr} "${pro1[2]:,}" | "${pro2[2]:,}"\nProfit per flight (\'Easy\'):{fe} "${pro1[3]:,}" | "${pro2[3]:,}"\n'
                   f'Flights per day (\'Easy\'):{de} "{round(pro1[4], 2)}" | "{round(pro2[4], 2)}"\nProfit per day (\'Easy\'):{pe} "${pro1[5]:,}" | "${pro2[5]:,}"```')
        else:
            msg = (f'```ml\nPrice:{ps} "${ac1[8]} M" | "${ac2[8]} M"\nCapacity:{cs} "{ac1[6]} pax" | "{ac2[6]} pax"\n'
                   f'Range:{rs} "{ac1[2]} km" | "{ac2[2]} km"\nSpeed:{ss} "{ac1[5]} km/h" | "{ac2[5]} km/h"\n'
                   f'Fuel Consumption:{fs} "{ac1[4]} lbs/km" | "{ac2[4]} lbs/km"\nCO2 Emmisions:{es} "{ac1[3]} kg/p/km" | "{ac2[3]} kg/p/km"\n'
                   f'Profit per flight (\'Realism\'):{fr} "${pro1[0]:,}" | "${pro2[0]:,}"\nFlights per day (\'Realism\'):{dr} "{round(pro1[1], 2)}" | "{round(pro2[1], 2)}"\n'
                   f'Profit per day (\'Realism\'):{pr} "${pro1[2]:,}" | "${pro2[2]:,}"\nProfit per flight (\'Easy\'):{fe} "${pro1[3]:,}" | "${pro2[3]:,}"\n'
                   f'Flights per day (\'Easy\'):{de} "{round(pro1[4], 2)}" | "{round(pro2[4], 2)}"\nProfit per day (\'Easy\'):{pe} "${pro1[5]:,}" | "${pro2[5]:,}"```')

        
        embed = discord.Embed(title=f"{ac1[1]} vs. {ac2[1]}", colour=discord.Colour(0xff9900))

        embed.set_image(url=f"https://www.airline4.net/assets/img/aircraft/png/{ac1[9]}.png")
        embed.set_footer(text="Data and Profit Formula provided by Scuderia Airlines' AC database.")
        embed.add_field(name = 'Comparison', value = msg)
        
        message = await ctx.send('', embed = embed)
        await message.add_reaction('🇲')
        await message.add_reaction('🦵')
            

@bot.command(help = 'Shows info of a selected airport. Usage: $airport <IATA or ICAO code of selected airport>', brief = 'Shows info of a selected airport.', enabled = True)
async def airport(ctx, code):
    if paused == False:
        counter('airport')
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

@bot.command()
async def search(ctx, value, thansign = '>' ,column = 'cost', orderby = 'cost', direction = 'desc'):
    if paused == False:
        counter('search')
        succ = True
        if thansign == '>':
            thansign = '<='
        elif thansign == '<':
            thansign = '>='
        else:
            await ctx.send('invalid than sign')
            succ = False

        if direction != 'asc' and direction != 'desc':
            await ctx.send(f'Formatting error.')
            succ = False
        
        try:
            if len(value) >= 5:
                value = float(value) / 1000000
            elif float(value) < 0:
                await ctx.send('Value negative. Planes are never free!')
            else:
                value = float(value)
        except:
            await ctx.send(f'Value not a number.')
        output = ''
        injection = False
        try:
            acdb.reconnect(attempts = 5, delay = 0.5)
            if succ:
                cursor.execute(f"SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `shortname`, `cost` FROM `am4bot` WHERE `{column}` {thansign} {float(value)} AND `type` = 'pax' ORDER BY `{orderby}` {direction.upper()} LIMIT 10")
            acdb.close()
        except mysql.connector.Error as error:
            if error.errno == 1054:
                await ctx.send(f"Unknown column. Columns available are: ```'cost', 'cap', 'rng', 'spd', 'fuel', 'co2'```")
            elif error.errno == 1064:
                await ctx.send(f'Formatting error.')
            else:
                await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')
            succ = False
        embed = discord.Embed(title = f'Showing planes where **{column}** {thansign} **{value}**, ordered by {orderby}:', colour = discord.Colour(0x33b300))
        embed.set_footer(text="Data and Profit Formula provided by Scuderia Airlines' AC database.")
        for ac in cursor:
            embed.add_field(name = f'{ac[1]} ($info {ac[7]})', value = f'```py\n${ac[8]}M; {ac[6]} pax; {ac[2]}km; {ac[5]}km/h; {ac[4]}l/km```', inline = False)
        if succ:
            await ctx.send(embed = embed)

@bot.command(aliases = ['user'])
@commands.cooldown(60, 86400)
async def airline(ctx, *, airline = ''):
    if not paused:
        counter('airline')
        if airline == '':
            airline = ctx.author.display_name
        airline = quote(airline)
        with urlopen(f'https://www.airline4.net/api/?access_token=***REMOVED***&user={airline}') as file:
            data = json.load(file)
        if data['status']['request'] == 'success':
            embed = discord.Embed(title = f"Airline data for {data['user']['company']}", colour = discord.Colour(0x1924bf))
            embed.set_footer(text="Data updated live from the AM4 API.")
            embed.add_field(name = 'Mode:', value = data['user']['game_mode'])
            embed.add_field(name = 'Alliance:', value = data['user']['alliance'])
            embed.add_field(name = 'Share Value:', value = f"${data['user']['share']}")
            embed.add_field(name = 'Level:', value = data['user']['level'])
            embed.add_field(name = 'Fleet:', value = data['user']['fleet'])
            embed.add_field(name = 'Routes:', value = data['user']['routes'])
            embed.add_field(name = 'Achievements:', value = f"{data['user']['achievements']}/71")
            embed.add_field(name = 'Shares Sold:', value = f"{data['user']['shares_sold']}/{data['user']['shares_sold']+data['user']['shares_available']}")
            embed.add_field(name = 'Company Founded: ', value = strftime('%d. %m. %Y', gmtime(data['user']['founded'])))
            embed.add_field(name = 'Last online:', value = strftime('%d. %m. %Y, %H:%M GMT', gmtime(data['user']['online'])))
            await ctx.send('', embed = embed)
        else:
            await ctx.send(f'API Error: {data["status"]["description"]}')

@bot.command()
@commands.cooldown(100, 86400)
async def fleet(ctx, *, airline = ''):
    if not paused:
        counter('fleet')
        message = await ctx.send('Calculating, Please Wait...')
        total = 0
        fleet = 0
        bumsecks = 0
        if airline == '':
            airline = ctx.author.display_name
        airline = quote(airline)
        with urlopen(f'https://www.airline4.net/api/?access_token=***REMOVED***&user={airline}') as file:
            data = json.load(file)
        if data['status']['request'] == 'success':
            if data['user']['game_mode'] == 'Realism':
                mode = 2
            else:
                mode = 5
            embed = discord.Embed(title = f'Fleet of {data["user"]["company"]}', colour = discord.Colour(0xffee00))
            embed.set_footer(text="Data updated live from the AM4 API.\nData and Profit Formula provided by Scuderia Airlines' AC database.")
            for fleet in data['fleet']:
                succ = False
                ac = fleet['aircraft']
                try:
                    acdb.reconnect(attempts = 5, delay = 0.5)
                    cursor.execute(f"SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type` FROM `am4bot` WHERE `model` = '{ac}'")
                except mysql.connector.Error as error:
                    await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')
                for plane in cursor:
                    succ = True
                    if plane[10] == 'Pax':
                        pro = profit(plane)
                    else:
                        pro = procargo(plane)
                    ac = plane[1]
                if not succ:
                    await ctx.send(f'This command is being tested. It would seem that your {ac} is mis-named in the database. Contact <@208900223504875521> to edit it.')
                    embed.add_field(name = 'Plane:', value = f'**{ac}** x {fleet["amount"]}')
                else:
                    total += pro[mode]*fleet["amount"] 
                    embed.add_field(name = 'Plane:', value = f'**{ac}** x {fleet["amount"]} | Max Profit: **${pro[mode]*fleet["amount"]:,}**', inline = False)
                bumsecks += fleet['amount']
            embed.add_field(name = 'Fleet', value = f"Total Planes: **{bumsecks}**")
            embed.add_field(name = 'Profit', value = f"Total Ideal Profit per Day: **${total:,}**")
            await message.edit(content = '', embed = embed)
            acdb.close()
        else:
            await message.edit(content = f'API Error: {data["status"]["description"]}')
        
def correct_channel(ctx):
    return ctx.message.channel.id == 554503485765189642, 484644663471636481
try:
    with open('ass.json') as infile:
        shit = json.load(infile)
except:
    shit = None
    print('PGS not enabled.')

kill = False

@bot.command()
@commands.has_role(689497556639547435)
@commands.check(correct_channel)
@commands.cooldown(1, 900)
async def price(ctx, *cost):
    counter('price')
    if kill == False:
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
            if fuel <= 900 or co2 <= 140:
                await role.edit(mentionable = True)
                await ctx.send(output + role.mention + f" (Price sent by {ctx.message.author.mention})")
                await role.edit(mentionable = False)
            elif output != f"":
                await ctx.send(output + f"(Price sent by {ctx.message.author.mention})")
            else:
                pass
        
        shit[f'{time()}'] = {'fuel' : f'{fuel}', 'co2' : f'{co2}'}
        with open('ass.json', 'w') as outfile:
            json.dump(shit, outfile)
    
        await ctx.message.delete()
        
        
@bot.command(hidden = True)
@commands.has_role(646148607636144131)
async def killswitch(ctx):
    kill = not kill

@bot.command()
async def stats(ctx):
    await ctx.send('Usage (Since Last Reset):```ml\nInfo: ' + str(infoC) + '\nCompare: ' + str(compareC) + '\nSearch: ' + str(searchC) + '\nSeeall: ' + str(seeallC) + '\nPrice: ' + str(priceC) + '\nWebsite: ' + str(websiteC) + '\nSheet: ' + str(sheetC) + '\nAirport: ' + str(airportC) + '\nAirline: ' + str(airlineC) + '\nFleet: ' + str(fleetC) + '```')
    
    
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

@bot.command(aliases = ['botinfo'], hidden = True)
async def version(ctx):
    if paused == False:
        await ctx.send(botinfo + '\nJoin our bot support server: https://discord.gg/4tVQHtf')

paused = False
@bot.command(aliases = ['paused'])
@commands.has_role(646148607636144131)
async def pause(ctx):
    global paused
    if paused:
        await ctx.send('Bot has been resumed')
    else:
        await ctx.send('Bot has been suspended')
    paused = not paused

    
bot.run('***REMOVED***')

