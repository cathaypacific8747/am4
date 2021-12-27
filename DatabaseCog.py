info = 'Database Commands Extension v2.0'

import discord
from discord.ext import commands
from checks import *
import mysql.connector

acdb = mysql.connector.connect(user='***REMOVED***',
                               passwd='***REMOVED***',
                               host='***REMOVED***',
                               database='***REMOVED***')

cursor = acdb.cursor(buffered = True)

infoC = compareC = searchC = seeallC = 0
ac = ac1 = ac2 = pro1 = pro2 = msg = pro = embed = ps = cs = rs = ss = fs = es = fr = dr = pr = fe = de = pe = ''

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

def addspaces(prm, amt):
    out = ""
    prm = str(prm)
    tamt = amt - len(prm)
    for i in range(tamt):
        i = i
        out += " "
    return out

class DatabaseCog(commands.Cog, name = 'ACDB Commands'):
    def __init__(self, bot):
        self.bot = bot
        print(f'Loaded {info}!')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
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

    '''
    Public use:
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    $seeall|all|allac
    $info|ac
    $compare
    $search
    '''

    @commands.command(aliases = ['all', 'allac'], help='Links to a spreadsheet containing all short names of AC to be used with the $info command', brief='Sends all short names of AC', usage='$seeall|all|allac', hidden = True)
    @notPriceAlert()
    @notDM()
    async def seeall(self, ctx):
        global seeallC
        seeallC += 1
        s = "Here's a link to all to all AC shortnames. There are to be used in almost all commands:\n"
        s += "https://docs.google.com/spreadsheets/u/3/d/e/2PACX-1vTxa5kKsfJQe7Q8A_WzOOUC0NzHe2CGNMTEcZjnCMih04KF1ieSq2tWIpkTb2dgs6nxRw0lplNFa5bP/pubhtml\n"
        s += "To automatically search for aircraft abbreviations, use `$search`."
        await ctx.send(s)
        # await ctx.send(f'$seeall is now deprecated. Use the $search command instead.')
    @commands.command(aliases = ['ac'], help='Sends stats of a selected AC. Usage: $info <short name of an AC>', brief='Sends stats of a selected AC', usage='$info|ac <aircraftCode>')
    @notPriceAlert()
    @notDM()    
    async def info(self, ctx, plane):
        global infoC, ac, msg1, msg2, pro, embed1, embed2
        infoC += 1
        succ = False
        injection = False
        if "'" in plane:
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

            embed1.set_thumbnail(url='https://cdn.discordapp.com/attachments/659878639461990401/702476944414867506/plane.png')
            embed1.set_image(url=f"https://www.airline4.net/assets/img/aircraft/png/{ac[9]}.png")
            embed1.set_footer(text="Data and Profit Formula provided by Scuderia Airlines' AC database.\nSupport us by donating! For more info, use the $donate command.")
            
            embed2 = discord.Embed(title=f"{ac[1]}", colour=discord.Colour(0xd1021b))

            embed2.set_thumbnail(url='https://cdn.discordapp.com/attachments/659878639461990401/702474176489062410/maintlogo.png')
            embed2.set_image(url=f"https://www.airline4.net/assets/img/aircraft/png/{ac[9]}.png")
            embed2.set_footer(text="Data and Profit Formula provided by Scuderia Airlines' AC database.\nSupport us by donating! For more info, use the $donate command.")
            
            # sorry, had to change the format, it looks unorganised at first.
            # no problem my man.
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

    @commands.command(help='Compares two selected AC stats back to back. Usage: $compare <AC1> <AC2>', brief='Compares two selected AC stats back to back', usage='$compare <aircraftCode> <aircraftCode>')
    @notPriceAlert()
    @notDM()
    async def compare(self, ctx, plane1, plane2):
        global compareC, msg, embed, ac1, ac2, pro1, pro2, ps, cs, rs, ss, fs, es, fr, dr, pr, fe, de, pe
        compareC += 1
        succ1 = False
        succ2 = False
        injection = False
        if "'" in plane1[0] or "'" in plane2[0]:
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
            acdb.close()
        if injection == True:
            await ctx.send('SQL Injection detected. Stop it. Bad.')
            return
        if not succ1 and not succ2:
            await ctx.send('Neither of the aircraft found. You can see all AC abbreviations with the command $seeall')    
            return
        elif not succ1:
            await ctx.send('First aircraft not found. You can see all AC abbreviations with the command $seeall')
            return
        elif not succ2:
            await ctx.send('Second aircraft not found. You can see all AC abbreviations with the command $seeall')
            return
        elif ac1[10] != ac2[10]:
            await ctx.send("Can't compare cargo and pax aircraft")
            return
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

        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/659878639461990401/702476935376404550/compare.png')
        embed.set_image(url=f"https://www.airline4.net/assets/img/aircraft/png/{ac1[9]}.png")
        embed.set_footer(text="Data and Profit Formula provided by Scuderia Airlines' AC database.\nSupport us by donating! For more info, use the $donate command.")
        embed.add_field(name = 'Comparison', value = msg)
        
        message = await ctx.send('', embed = embed)
        await message.add_reaction('📱')
        await message.add_reaction('🦵')

    
    @commands.command(brief='Searches the database for aircrafts with the matching name.', usage='$search <name1> [name2] ...', help='Returns all aircrafts with its model name containing name1, name2, etc.\nThe names inputted are order-sensitive.')
    @notPriceAlert()
    @notDM()
    async def search(self, ctx, *args):
        global searchC
        searchC += 1
        if "'" in args:
            await ctx.send('SQL Injection detected. Stop it. Bad.')
            return
        if len(args) == 0:
            await ctx.send('Missing arguments, check `$help search` for more information.')
            return

        query = ''.join([f'%{i}%' for i in args])

        try:
            acdb.reconnect(attempts = 5, delay = 0.5)
            cursor.execute(f"SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type`, `shortname` FROM `am4bot` WHERE `aircraft` LIKE '{query}' ORDER BY `aircraft`")
        except mysql.connector.Error as error:
            await ctx.send(f'Database error. Contact <@243007616714801157> if this happens.```python\n{error}```')    
        acdb.close()

        embed = discord.Embed(title = f"Results for **{''.join([f'{i} ' for i in args])}**", colour = discord.Colour(0x03fce3))
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/659878639461990401/799226240305332224/search_icon.png')
        embed.set_footer(text="Data provided by Scuderia Airlines' AC database.\nSupport us by donating! For more info, use the $donate command.")
        for result in cursor:
            if len(embed.fields) <= 24:
                isCargo = result[10] == 'Cargo'
                icon = '<:cargo:773841095896727573>' if isCargo else '<:pax:773841110271393833>'
                embed.add_field(name = f"{result[1]} {icon}", value = f"```ml\n${result[8]} M, {result[6]:,} {'lbs' if isCargo else 'pax'}, {result[4]} lbs/km```**Call with:** $info {result[11]}\n", inline = False)
        if len(embed.fields) == 0:
            embed.add_field(name = ":x: No aircraft found!", value = f"No entry found containing given searchword{'' if len(args) == 1 else 's'}. Make sure there are no misspellings. {'' if len(args) == 1 else 'Remember that this command is **order sensitive**, that means multiple searchwords must be given in order!'}")
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(DatabaseCog(bot))