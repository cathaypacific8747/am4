V = 'v3.5.1'
botinfo = (f'**AM4 ACDB bot** {V}\n'
           f'made by **favorit1**, maintained by **Cathay Express**\n'
           f'database and profit formula by **Scuderia Airlines**')

import discord
from discord.ext import commands, tasks
import csv
import math
from copy import deepcopy

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

infoC, compareC, searchC, seeallC, priceC, websiteC, sheetC, airportC, fleetC, airlineC = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
def counter(cmd):
    global infoC, compareC, searchC, seeallC, priceC, websiteC, sheetC, airportC, fleetC, airlineC
    if cmd == 'info': infoC += 1
    elif cmd == 'compare': compareC += 1
    elif cmd == 'search': searchC += 1
    elif cmd == 'seeall': seeallC += 1
    elif cmd == 'price': priceC += 1
    elif cmd == 'website': websiteC += 1
    elif cmd == 'sheet': sheetC += 1
    elif cmd == 'airport': airportC += 1
    elif cmd == 'fleet': fleetC += 1
    elif cmd == 'airline': airlineC += 1
        
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

@bot.command(aliases = ['tools', 'web'], help='Links to Scuderia\'s AM4 Tools Website')
async def website(ctx):
    if not paused:
        counter('website')
        await ctx.send(f'Here\'s the link to the AM4 Tools Website, created by Scuderia Airlines:\nhttps://scuderiaairlines.github.io/AM4-Guides-and-Tools/index.html')

@bot.command(aliases = ['excel', 'sheet'], help='Links to the AM4 AC Spreadsheet')
async def spreadsheet(ctx):
    if paused == False:
        counter('sheet')
        msg = "Here's the link to the AM4 AC spreadsheet, created by Scuderia Airlines, and the rest of the Guide Development team:" + '\n'
        msg += 'https://docs.google.com/spreadsheets/d/1YInKDK8fHmetOO1n9ZSyn8--gZhNmsY6BIjBoEhInTQ/edit?usp=sharing'
        await ctx.send(msg)
    
@bot.command(aliases = ['all', 'allac'], help='Links to a spreadsheet containing all short names of AC to be used with the $info command', brief='Sends all short names of AC')
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
    global msg, msg2, ac, pro, embed, embed1, embed2, ps, cs, rs, ss, fs, es, fr, dr, pr, fe, de, pe, ac1, ac2, pro1, pro2
    if user == reaction.message.author:
        pass
    elif str(reaction.emoji) == '📱':
        ps = cs = rs = ss = fs = es = fr = dr = pr = fe = de = pe = '\n'
        if ac[10] == 'Cargo':
            try:
                msg1 = (f'```ml\nPrice:\n"{ac[8]} million"\nCapacity:\n"{ac[6]:,} lbs"\nRange:\n"{ac[2]} KM"\n'
                        f'Speed:\n"{ac[5]} KM/h"\nFuel consumption:\n"{ac[4]} lbs/KM"\nCO2 emmisions:\n"{ac[3]} kg/1k lbs/KM"```')
            except:
                pass
        elif ac1[10] == 'Cargo':
            try:
                msg = (f'```ml\nPrice:{ps} "${ac1[8]} M" | "${ac2[8]} M"\nCapacity:{cs} "{ac1[6]:,} lbs" | "{ac2[6]:,} lbs"\n'
                       f'Range:{rs} "{ac1[2]} KM" | "{ac2[2]} KM"\nSpeed:{ss} "{ac1[5]} KM/h" | "{ac2[5]} KM/h"\n'
                       f'Fuel Consumption:{fs} "{ac1[4]} lbs/KM" | "{ac2[4]} lbs/KM"\nCO2 Emmisions:{es} "{ac1[3]} kg/k/km" | "{ac2[3]} kg/k/km"\n'
                       f'Profit per flight (\'Realism\'):{fr} "${pro1[0]:,}" | "${pro2[0]:,}"\nFlights per day (\'Realism\'):{dr} "{round(pro1[1], 2)}" | "{round(pro2[1], 2)}"\n'
                       f'Profit per day (\'Realism\'):{pr} "${pro1[2]:,}" | "${pro2[2]:,}"\nProfit per flight (\'Easy\'):{fe} "${pro1[3]:,}" | "${pro2[3]:,}"\n'
                       f'Flights per day (\'Easy\'):{de} "{round(pro1[4], 2)}" | "{round(pro2[4], 2)}"\nProfit per day (\'Easy\'):{pe} "${pro1[5]:,}" | "${pro2[5]:,}"```')
            except:
                pass
        else:
            try:
                msg1 = (f'```ml\nPrice: \n"{ac[8]} million"\nCapacity: \n"{ac[6]} pax"\nRange: \n"{ac[2]} km"\n'
                        f'Speed: \n"{ac[5]} km/h"\nFuel consumption: \n"{ac[4]} lbs/km"\nCO2 emmisions: \n"{ac[3]} kg/pax/km"```')
            except:
                pass
            try:
                msg = (f'```ml\nPrice:{ps} "${ac1[8]} M" | "${ac2[8]} M"\nCapacity:{cs} "{ac1[6]} pax" | "{ac2[6]} pax"\n'
                       f'Range:{rs} "{ac1[2]} km" | "{ac2[2]} km"\nSpeed:{ss} "{ac1[5]} km/h" | "{ac2[5]} km/h"\n'
                       f'Fuel Consumption:{fs} "{ac1[4]} lbs/km" | "{ac2[4]} lbs/km"\nCO2 Emmisions:{es} "{ac1[3]} kg/p/km" | "{ac2[3]} kg/p/km"\n'
                       f'Profit per flight (\'Realism\'):{fr} "${pro1[0]:,}" | "${pro2[0]:,}"\nFlights per day (\'Realism\'):{dr} "{round(pro1[1], 2)}" | "{round(pro2[1], 2)}"\n'
                       f'Profit per day (\'Realism\'):{pr} "${pro1[2]:,}" | "${pro2[2]:,}"\nProfit per flight (\'Easy\'):{fe} "${pro1[3]:,}" | "${pro2[3]:,}"\n'
                       f'Flights per day (\'Easy\'):{de} "{round(pro1[4], 2)}" | "{round(pro2[4], 2)}"\nProfit per day (\'Easy\'):{pe} "${pro1[5]:,}" | "${pro2[5]:,}"```')
            except:
                pass
        try:
            msg2 = (f'```ml\nMin. Runway Required: \n"{int(ac[11]):,} ft"\nFl. Hours Before Check: \n"{int(ac[12])} Hours"\nA-Check Cost: \n"${ac[13]}"\n'
                    f'Profit per Flight (\'Realism\'): \n"${pro[0]:,}"\nFlights per day (\'Realism\'): \n"{round(pro[1], 2)}"\nProfit per Day (\'Realism\'): \n"${pro[2]:,}"\n'
                    f'Profit per Flight (\'Easy\'): \n"${pro[3]:,}"\nFlights per day (\'Easy\'): \n"{round(pro[4], 2)}"\nProfit per Day (\'Easy\'): \n"${pro[5]:,}"```')
        except:
            pass
    
        embed1.set_field_at(0, name = 'Brief Statistics (Mobile)', value = msg1)
        embed2.set_field_at(0, name = 'Extra Statistics and Profit (Mobile)', value = msg2)
        embed.set_field_at(0, name = 'Comparison (Mobile)', value = msg)
        print(reaction.message.embeds[0].colour)
        if reaction.message.embeds[0].colour == discord.Colour(0xd0021b):
            await reaction.message.edit(embed = embed1)
        elif reaction.message.embeds[0].colour == discord.Colour(0xd1021b):
            await reaction.message.edit(embed = embed2)
        else:
            await reaction.message.edit(embed = embed)
    elif str(reaction.emoji) == '🦵':
        content = reaction.message.embeds[0].fields[0].value
        await reaction.message.edit(content = content, suppress = True)
    elif str(reaction.emoji) == '⏩':
        await reaction.clear()
        await reaction.message.edit(embed = embed2)
        await reaction.message.add_reaction('⏪')
    elif str(reaction.emoji) == '⏪':
        await reaction.clear()
        await reaction.message.edit(embed = embed1)
        await reaction.message.add_reaction('⏩')
        
        
ac = ac1 = ac2 = pro1 = pro2 = msg = pro = embed = ps = cs = rs = ss = fs = es = fr = dr = pr = fe = de = pe = ''
@bot.command(aliases = ['ac'], help='Sends stats of a selected AC. Usage: $info <short name of an AC>', brief='Sends stats of a selected AC')
async def info(ctx, plane):
    if paused == False:
        global ac, msg1, msg2, pro, embed1, embed2
        counter('info')
        succ = False
        injection = False
        if plane[0] == "'":
            injection = True
        if injection == False:
            try:
                acdb.reconnect(attempts = 5, delay = 0.5)
                cursor.execute(f"SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type`, `rwy`, `maint`, `acost` FROM `am4bot` WHERE `shortname` = '{plane}'")
                acdb.close()
            except mysql.connector.Error as error:
                await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')
        for ac1 in cursor:
            ac = ac1
            embed1 = discord.Embed(title=f"{ac[1]}", colour=discord.Colour(0xd0021b))

            embed1.set_image(url=f"https://www.airline4.net/assets/img/aircraft/png/{ac[9]}.png")
            embed1.set_footer(text="Data and Profit Formula provided by Scuderia Airlines' AC database.")
            
            embed2 = discord.Embed(title=f"{ac[1]}", colour=discord.Colour(0xd1021b))

            embed2.set_image(url=f"https://www.airline4.net/assets/img/aircraft/png/{ac[9]}.png")
            embed2.set_footer(text="Data and Profit Formula provided by Scuderia Airlines' AC database.")
            
            # sorry, had to change the format, it looks unorganised at first.
            if ac[10] == "Cargo":
                pro = procargo(ac1)
                msg1 = '```ml' + '\n'
                msg1 += f'           Price: "{ac[8]} million"' + '\n'
                msg1 += f'        Capacity: "{ac[6]:,} lbs"'   + '\n'
                msg1 += f'           Range: "{ac[2]} km"'      + '\n'
                msg1 += f'           Speed: "{ac[5]} km/h"'    + '\n'
                msg1 += f'Fuel consumption: "{ac[4]} lbs/km"'  + '\n'
                msg1 += f'   CO2 emmisions: "{ac[3]} kg/1k lbs/km"```'
                embed1.add_field(name = 'Brief Statistics', value = msg1)
                       
            else:
                pro = profit(ac1)
                msg1 = '```ml' + '\n'
                msg1 += f'           Price: "{ac[8]} million"' + '\n'
                msg1 += f'        Capacity: "{ac[6]} pax"'     + '\n'
                msg1 += f'           Range: "{ac[2]} km"'      + '\n'
                msg1 += f'           Speed: "{ac[5]} km/h"'    + '\n'
                msg1 += f'Fuel consumption: "{ac[4]} lbs/km"'  + '\n'
                msg1 += f'   CO2 emmisions: "{ac[3]} kg/pax/km"```'
                embed1.add_field(name = 'Brief Statistics', value=msg1)

            msg2 = '```ml' + '\n'
            msg2 += f'         Min. Runway Required: "{int(ac[11]):,} ft"'  + '\n'
            msg2 += f'       Fl. Hours Before Check: "{int(ac[12])} Hours"' + '\n'
            msg2 += f'                 A-Check Cost: "${ac[13]}"'           + '\n'
            msg2 += '\n'
            msg2 += f'Profit per Flight (\'Realism\'): "${pro[0]:,}"'        + '\n'
            msg2 += f'  Flights per day (\'Realism\'): "{round(pro[1], 2)}"' + '\n'
            msg2 += f'   Profit per Day (\'Realism\'): "${pro[2]:,}"'        + '\n'
            msg2 += f'   Profit per Flight (\'Easy\'): "${pro[3]:,}"'        + '\n'
            msg2 += f'     Flights per day (\'Easy\'): "{round(pro[4], 2)}"' + '\n'
            msg2 += f'      Profit per Day (\'Easy\'): "${pro[5]:,}"```'
            embed2.add_field(name = 'Extra Statistics and Profit', value=msg2)
            
            message = await ctx.send(embed = embed1)
            await message.add_reaction('📱')
            await message.add_reaction('🦵')
            await message.add_reaction('⏩')

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
        i = i
        out += " "
    return out
        
@bot.command(help='Compares two selected AC stats back to back. Usage: $compare <AC1> <AC2>', brief='Compares two selected AC stats back to back')
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

        ###  Consider using tabulate, plain, makes the code much more readable and maintainable.  ###
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
        await message.add_reaction('📱')
        await message.add_reaction('🦵')
            

@bot.command(help='Shows info of a selected airport. Usage: $airport <IATA or ICAO code of selected airport>', brief='Shows info of a selected airport', enabled = True)
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

@bot.command(help='Searches the DB for AC within given parameters')
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
        injection = False
        try:
            acdb.reconnect(attempts = 5, delay = 0.5)
            if succ and not injection:
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

@bot.command(aliases = ['user'], help='Shows some basic stats of an airline')
@commands.cooldown(200, 86400)
async def airline(ctx, *, airline = '', raw = False):
    if not paused:
        global embed1, embed2
        counter('airline')
        if airline == '':
            airline = ctx.author.display_name
        if not raw:
            airline = quote(airline)
        with urlopen(f'https://www.airline4.net/api/?access_token=***REMOVED***&user={airline}') as file:
            data = json.load(file)
        if data['status']['request'] == 'success':
            embed1 = discord.Embed(title = f"Airline data for {data['user']['company']}", colour = discord.Colour(0x1924bf))
            embed1.set_footer(text=f"Data updated live from the AM4 API; requests remaining: {data['status']['requests_remaining']}")
            embed1.add_field(name = 'Mode:', value = data['user']['game_mode'])
            embed1.add_field(name = 'Alliance:', value = data['user']['alliance'])
            # if int(data['user']['ipo']): # if performed ipo:
            embed1.add_field(name = 'Share Value:', value = f"${data['user']['share']}")
            embed1.add_field(name = 'Level:', value = data['user']['level'])
            embed1.add_field(name = 'Fleet:', value = data['user']['fleet'])
            embed1.add_field(name = 'Routes:', value = data['user']['routes'])
            embed1.add_field(name = 'Achievements:', value = f"{data['user']['achievements']}/72")
            embed1.add_field(name = 'Shares Sold:', value = f"{data['user']['shares_sold']}/{data['user']['shares_sold']+data['user']['shares_available']}")
            embed1.add_field(name = 'Company Founded: ', value = strftime('%d. %m. %Y', gmtime(data['user']['founded'])))
            embed1.add_field(name = 'Last online:', value = strftime('%d/%m/%y %H:%M GMT', gmtime(data['user']['online'])))
            message = await ctx.send('', embed = embed1)
            if data['user']['alliance'] != False:
                input = quote(data['user']['alliance'])
                with urlopen(f'https://www.airline4.net/api/?access_token=***REMOVED***&search={input}') as file:
                    alliance = json.load(file)
                embed2 = discord.Embed(title = f"Alliance data for {data['user']['company']}", colour = discord.Colour(0x216bd1))
                embed2.set_footer(text=f"Data updated live from the AM4 API; requests remaining: {alliance['status']['requests_remaining']}")
                msg = (f"```ml\nRank: #{alliance['alliance'][0].get('rank')}\n"
                       f"Member Count: {alliance['alliance'][0].get('members')}/{alliance['alliance'][0].get('maxMembers')}\n"
                       f"Share Value: {alliance['alliance'][0].get('value')}```")
                embed2.add_field(name = f"{alliance['alliance'][0].get('name')} brief data:", value = msg, inline = False)
                for member in alliance['members']: #pulls member data from alliance
                    if member['company'] == data['user']['company']:
                        user = member
                ago = round((time() - user['joined']) / 86400)
                embed2.add_field(name = 'Joined:', value = f"{ago} days ago\n({strftime('%d/%m/%y/ %H:%M GMT', gmtime(user['joined']))})")
                embed2.add_field(name = 'Flights:', value = user['flights'])
                embed2.add_field(name = 'Contributed:', value = f"${user['contributed']}")
                embed2.add_field(name = 'Contributed per Day:', value = f"${round(user['contributed'] / ago)}")
                await message.add_reaction('⏩')
        else:
            await ctx.send(f'API Error: {data["status"]["description"]}')

@bot.command(help='Shows an airline\'s fleet and the total ideal profit')
@commands.cooldown(200, 86400)
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
            embed.set_footer(text=f"Data updated live from the AM4 API; requests remaining: {data['status']['requests_remaining']}\nData and Profit Formula provided by Scuderia Airlines' AC database.")
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

@bot.command(hidden = True)
async def login(ctx, *, airline):
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
'''with open('data/ap-indexed-radians.csv', newline='', encoding='utf-8-sig') as f:
    global airports
    airports = list(csv.reader(f))

with open('data/ac-indexed.csv', newline='', encoding='utf-8-sig') as f:
    global aircrafts
    aircrafts = list(csv.reader(f))
'''
def calcCargoConfig(lh, maxCap, fPerDay):
    maxCap = int(maxCap)
    l = int(lh[0]) / int(fPerDay)
    h = int(lh[1]) / int(fPerDay)

    lCap = maxCap * 0.7 if (int(lh[0]) / 0.7 > maxCap * int(fPerDay)) else l # if demand > capacity, set full large.
    lPct = int(lCap / maxCap / 0.7 * 100) / 100
    hCap = maxCap * (1 - lPct)
    if h >= hCap: # if there is excess demand
        return [lPct, int(100 * (1 - lPct)) / 100]
    else: # hDemand too small, depleted easily, return nothing
        return [0, 0]

def calcFirstPrioritizedSeats(yjf, maxSeats, fPerDay):
    y = int(yjf[0]) / int(fPerDay)
    j = int(yjf[1]) / int(fPerDay)
    f = int(yjf[2]) / int(fPerDay)

    fS = int(maxSeats / 3) if (f*3 > maxSeats) else int(f)
    jS = int((maxSeats - (fS*3)) / 2) if ((j*2 + f*3) > maxSeats) else int(j)
    yS = maxSeats - fS*3 - jS*2

    if (yS * fPerDay) < y:
        return [yS, jS, fS]
    else:
        return [0, 0, 0]

def distanceCoor(lat1, lon1, lat2, lon2): # radians
    return 12742 * math.asin(math.sqrt(math.pow(math.sin((lat2-lat1) / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin((lon2-lon1) / 2), 2)))

def findStopover(oName, dName, shortName, isRealism=False): # None = malformed input
    o, d, range, rwyReq = [], [], -1, 0 # in case if airport is not found

    ##  get aircraftRange and minRwy whenever possible  ##
    for ac in aircrafts:
        if ac[1] == shortName:
            fullName = ac[2] + ' ' + ac[3]
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

        stpvrCandidates.sort(key=lambda x:x[9]+x[10])

        stpvrCandidates = stpvrCandidates[0]
        if stpvrCandidates[9] + stpvrCandidates[9] == float('inf'):
            return 'UNREACHABLE'
        else:
            stpvrCandidates.extend([o[1], o[7], o[8], d[1], d[7], d[8], isCargo, range])
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

@bot.command(help='Finds the most distance-efficient stopover given inputs of aircraft, origin and destination.', brief='Finds the most distance-efficient stopover.')
async def stop(ctx, oName, dName, shortACname):
    realismRole = discord.utils.get(ctx.guild.roles, name='Realism')
    if realismRole in ctx.author.roles: 
        isRealism = True # user is Realism
        subheading = '**Realism**'
    else:
        isRealism = False
        subheading = '**Easy**'

    stpvr = findStopover(oName.upper(), dName.upper(), shortACname.lower(), isRealism)
    if stpvr == None:
        await ctx.send('Wrong inputs. See $help for proper command usage.')
    else:
        if stpvr != 'UNREACHABLE':
            isCargo, isMobile = stpvr[17], ctx.author.is_on_mobile()
            embed = discord.Embed(
                title=stpvr[11] + ' -- ' + stpvr[14], 
                colour=discord.Colour.dark_blue()
            )
            d = math.ceil(distanceCoor(float(stpvr[12]), float(stpvr[13]), float(stpvr[15]), float(stpvr[16])))
            t = tickets(d, isRealism, isCargo)

            if 1: # display details, don't mind me, just to make it collapsible
                value = '```ml\n'
                value += '    IATA: ' + stpvr[3] + '\n'
                value += '    ICAO: ' + stpvr[4] + '\n'
                if isRealism:
                    value += '  Runway: ' + stpvr[5] + ' FT\n'
                if isMobile:
                    value += 'Location: ' + stpvr[1] + ',\n'
                    value += '          ' + stpvr[2] + '\n'
                    value += 'Distance: ' + str(d) + ' KM' + '\n'
                    if isCargo:
                        value += ' Tickets: L [' + str(t[0]) + ']\n'
                        value += '          H [' + str(t[1]) + ']```'
                    else:
                        value += ' Tickets: Y [' + str(t[0]) + ']\n'
                        value += '          J [' + str(t[1]) + ']\n'
                        value += '          F [' + str(t[2]) + ']```'
                else: # desktop
                    value += 'Location: ' + stpvr[1] + ', ' + stpvr[2] + '\n'
                    value += 'Distance: ' + str(d) + ' KM' + '\n'
                    if isCargo: value += ' Tickets: L $[' + str(t[0]) + '], H $[' + str(t[1]) + ']```'
                    else:       value += ' Tickets: Y $[' + str(t[0]) + '], J $[' + str(t[1]) + '], F $[' + str(t[2]) + ']```'

                embed.add_field(name=subheading, value=value)
                embed.set_footer(text="Formulae provided by Scuderia Airlines.")
            await ctx.send(embed=embed)
        else:
            msg = '‎\u200B\n'
            msg += 'There are **no possible stopovers** for this route, in '+subheading+' mode.'
            await ctx.send(msg)

@bot.command(help='Shows the most profitable routes given the maximum distance and hub.\n For training-points-enhanced cargo load (1.06x capacity), add a "+" at the back of the <shortACname>.', brief='Finds the most profitable routes.')
async def routes(ctx, airportName, shortACname, targetDistance, flightsPerDay):
    capacityMod = 1.06 if '+' in shortACname else 1
    shortACname = shortACname.replace('+', '').lower()
    airportName = airportName.upper()

    isRealism = discord.utils.get(ctx.guild.roles, name='Realism') in ctx.author.roles # checks whether the user is Realism or not

    o, range, rwyReq, needsStopover = [], -1, 0, False # in case if airport is not found
    ##  get aircraftRange and minRwy whenever possible  ##
    for ac in aircrafts:
        if ac[1] == shortACname:
            fullName = ac[2] + ' ' + ac[3]
            range = int(ac[12])
            isCargo = bool(int(ac[19]))
            capacity = int(ac[10]) * capacityMod
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
            msg = f':warning:**Warning: **Target Distance ({targetDistance} km) is larger than the maximum stopover range of the aircraft ({range*2} km).' + '\n'
            msg += f'Now assuming your target distance to be **{range*2}** km.'
            await ctx.send(msg)
            targetDistance = range * 2
        if int(targetDistance) > range:
            # stopovers are needed, so set the flag
            needsStopover = True

        with open(f'data/dist/{o[0]}.csv', newline='', encoding='utf-8-sig') as f:
            data, filtered = list(csv.reader(f)), []
            embed = discord.Embed(
                title=f'{fullName} departing {o[1]}, {o[2]}',
                colour=discord.Colour.dark_blue()
            )

            for d in data:
                if int(d[9]) <= int(targetDistance) and int(d[8]) >= rwyReq:
                    filtered.append(d)

            for f in filtered:
                try:
                    if isCargo:
                        cargoCfg = calcCargoConfig([round(int(f[1])*500, -3), round(int(f[2])*1000, -3)], int(capacity), int(flightsPerDay)) # configuration in decimal percentages
                        ticketP = tickets(int(f[9]), isRealism, True) # cargo prices
                        maxIncome = ticketP[0] * (cargoCfg[0]*capacity*0.7) + ticketP[1] * (cargoCfg[1]*capacity)
                        f.extend([maxIncome, cargoCfg, ticketP])
                    else:
                        paxCfg = calcFirstPrioritizedSeats([int(f[1]), int(f[2]), int(f[3])], capacity, int(flightsPerDay)) # pax in pure seats
                        ticketP = tickets(int(f[9]), isRealism, False) # pax prices
                        maxIncome = ticketP[0]*paxCfg[0] + ticketP[1]*paxCfg[1] + ticketP[2]*paxCfg[2]
                        f.extend([maxIncome, paxCfg, ticketP])
                except:
                    f.extend([0, [0, 0, 0], [0, 0, 0]])

            filtered.sort(key=lambda x:x[10], reverse=True)
            counter = 0

            for f in filtered:
                if int(f[10]) > 0: # income is +ve
                    val = '```ml\n'
                    try:
                        if needsStopover:
                            stop = findStopover(o[3], f[6], shortACname, isRealism) # calculate the stopover for that route
                            if stop != None and stop != 'UNREACHABLE': # add stopover to display
                                val += f'Stopover: {stop[1]}, {stop[2]}' + '\n'
                                val += f'          {stop[3]} | {stop[4]}' + '\n'
                            else:
                                raise ValueError('noStopovers')

                        if isCargo:
                            val += f'  Demand: L [{round(1000 * round(int(f[1])*0.5))}], H [{round(1000 * int(f[2]))}]' + '\n'
                            
                            val += f'  Config: L [{int(f[11][0] * 100)}%], H [{int(f[11][1] * 100)}%]' + '\n'
                            val += f' Tickets: L $[{f[12][0]}], H $[{f[12][1]}]' + '\n'
                        else:
                            val += f'  Demand: Y [{f[1]}], J [{f[2]}], F [{f[3]}]' + '\n'
                            val += f'  Config: Y [{f[11][0]}], J [{f[11][1]}], F [{f[11][2]}]' + '\n'
                            val += f' Tickets: Y $[{f[12][0]}], J $[{f[12][1]}], F $[{f[12][2]}]' + '\n'

                        if isRealism: 
                            val += f'  Runway: {f[8]} FT' + '\n'

                        val += f'Distance: {f[9]} KM' + '\n'                
                        val += f'  Income: $ {int(f[10]):,d}' + '\n'
                        val += '```'

                        embed.add_field(name=f'**{f[4]}**, {f[5]}\n{f[6]} | {f[7]}', value=val, inline=False)
                        counter += 1
                    except:
                        pass # don't even show the route if stopovers aren't possible
                if counter > 5:
                    break # stop the loop, as it has already displayed over 5 results
                    # just in case the possible routes are less than 5, the for loop would've finished already
            if counter == 0:
                embed.add_field(name='Error', value='There are no profitable routes.')
            embed.set_footer(text="Database and formulae provided by Scuderia Airlines and Cathay Express.")
            await ctx.send(embed=embed)

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
@bot.command(hidden=True)
@commands.has_role(646148607636144131)
async def killswitch(ctx):
    global kill
    kill = not kill
    await ctx.send('Notifications killed!')

@bot.command(help='Shows the number of command uses since last restart.')
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
    await ctx.send('Cooldown has been reset!')

@bot.command(aliases = ['botinfo'], hidden = True)
async def version(ctx):
    if paused == False:
        await ctx.send(botinfo + '\nJoin our bot support server: https://discord.gg/4tVQHtf')

paused = False
@bot.command(aliases = ['paused'], hidden = True)
@commands.has_role(646148607636144131)
async def pause(ctx):
    global paused
    if paused:
        await ctx.send('Bot has been resumed')
    else:
        await ctx.send('Bot has been suspended')
    paused = not paused

    
bot.run('***REMOVED***')