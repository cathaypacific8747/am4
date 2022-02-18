info = 'AM4 API Commands Extension v1.5.1'

import importlib # for reimporting imports
import graphgen # needed
from graphgen import svgraph, regressionGradient

import discord
from discord.ext import commands
import aiomysql
import mysql.connector
from urllib.request import urlopen
from urllib.parse import quote

from DatabaseCog import profit, procargo
from SettingsCog import discordSettings
from statistics import mean, median
import os
import urllib3
from time import gmtime, time, strftime
from io import BytesIO
from checks import *
import json
import re

airlineC, fleetC = 0, 0
AM4token = '***REMOVED***'

def GenAllianceEmbed():
    global data
    input = quote(data['user']['alliance'])
    with urlopen(f'https://www.airline4.net/api/?access_token={AM4token}&search={input}') as file:
        alliance = json.load(file)
    embed2 = discord.Embed(title = f"Alliance data for {data['user']['company']}", colour = discord.Colour(0x216bd1))
    embed2.set_footer(text=f"Data updated live from the AM4 API; requests remaining: {alliance['status']['requests_remaining']}\nSupport us by donating! For more info, use the $donate command.")
    msg = (f"```ml\nRank: #{alliance['alliance'][0].get('rank')}\n"
        f"Member Count: {alliance['alliance'][0].get('members')}/{alliance['alliance'][0].get('maxMembers')}\n"
        f"Share Value: {alliance['alliance'][0].get('value')}```")
    embed2.add_field(name = f"{alliance['alliance'][0].get('name')} brief data:", value = msg, inline = False)
    for member in alliance['members']: #pulls member data from alliance
        if member['company'] == data['user']['company']:
            user = member
    ago = round((time() - user['joined']) / 86400)
    embed2.add_field(name = 'Joined:', value = f"{ago} days ago\n({strftime('%d/%b/%y/ %H:%M GMT', gmtime(user['joined']))})")
    if user['joined'] <= 1584369000:
        ago = (time() - 1584369000) / 86400
    embed2.add_field(name = 'Flights:', value = f"{user['flights']:,}")
    embed2.add_field(name = 'Contributed:', value = f"${user['contributed']:,}")
    embed2.add_field(name = 'Avg. Contribution per Day:', value = f"${round(user['contributed'] / ago):,}")
    return embed2

def IncrementBar(bar):
    l = list(bar)
    l[-1] = ''
    l.insert(0, '▮')
    return ''.join(l)

class Logs:
    def __init__(self, username=None, allianceName=None):
        self.username = username
        self.allianceName = allianceName
    
    def saveInfo(self, data):
        dir = 'userLog' if self.username else 'allianceLog'
        with open(f'data/{dir}/index.json', 'r+') as f:
            mappings = json.load(f)
            for key in mappings:
                if mappings[key] == self.username:
                    targetKey = key
                    break
            else:
                # create a new mapping if not found
                targetKey = str(max([int(i) for i in list(mappings)])+1)
                mappings[targetKey] = self.username
                f.seek(0)
                json.dump(mappings, f, indent=4)
                f.truncate()
                os.mkdir(f'data/{dir}/{targetKey}')
                
        # log down the values with the specified mapping.
        with open(f'data/{dir}/{targetKey}/{int(time())}.json', 'w+') as f:
            json.dump(data, f, indent=4)

class AM4APICog(commands.Cog, name = 'API Commands'):
    def __init__(self, bot):
        self.bot = bot
        print(f'Loaded {info}!')
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global embed1
        if reaction.message.author == user:
            pass
        elif str(reaction) == '▶':
            await reaction.clear()
            await reaction.message.edit(embed = GenAllianceEmbed())
            await reaction.message.add_reaction('◀')
        elif str(reaction) == '◀':
            await reaction.clear()
            await reaction.message.edit(embed = embed1)
            await reaction.message.add_reaction('▶')

    '''
    Public use:
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    $user|airline
    $fleet
    '''

    @commands.command(aliases = ['airline'], help='Shows some basic stats of an airline', usage='$user|airline [optional: airline name/id]', intends = discord.Intents.default())
    @commands.cooldown(200, 86400)
    @notDM()
    @notPriceAlert()
    async def user(self, ctx, *, airline=''):
        global data
        global embed1, airlineC
        airlineC += 1

        useId = False
        if airline == '': # querying itself
            airline = ctx.author.display_name
            if '%' not in airline: airline = quote(airline)

            s = discordSettings(discordUserId=ctx.author.id).getUserSettings()
            if 'userid' in s:
                userId = s['userid']
                useId = True
        else:
            try:
                userId = int(airline)
                useId = True
            except: # if input airline is not int-able
                if str(airline)[-1] == '>': # is mentioning someone
                    try: 
                        #airline = ctx.guild.get_member(int(airline.replace('<@!', '').replace('>', '')))
                        UID = int(airline.replace('<@!', '').replace('>', ''))
                        s = discordSettings(discordUserId=UID).getUserSettings()
                        if 'userid' in s:
                            userId = s['userid']
                            useId = True
                        else:
                            #airline = airline.display_name
                            await message.edit(content = 'Error:\nCould not find this user. Try entering their nickname instead.')
                            return
                    except:
                        await message.edit(content = 'Error:\nCould not find this user.')
                airline = airline.replace('<s>', ' ').replace('࣪', ' ') # for space in front of airlines.
                if '%' not in airline: airline = quote(airline)

        url = f'https://www.airline4.net/api/?access_token={AM4token}&id={userId}' if useId else f'https://www.airline4.net/api/?access_token={AM4token}&user={airline}'
        loadingMessage = await ctx.send('Loading data...')
        http = urllib3.PoolManager()
        data = json.loads(http.request('GET', url).data.decode('utf-8'))
        if data['status']['request'] == 'success':
            # Logs(username=data['user']['company']).saveInfo(data) # save it for future use.
            embed1 = discord.Embed(title = f"Airline data for {data['user']['company']}", colour=discord.Colour(0x1924bf))
            embed1.set_footer(text=f"Data updated live from the AM4 API. Requests remaining: {data['status']['requests_remaining']}\nSupport us by donating! For more info, use the $donate command.")
            
            await loadingMessage.edit(content='Processing data...')
            hasIPO = bool(data['user']['share'])
            try:
                path = re.search("(?P<url>https?://[^\s]+)", data['user']['logo']).group("url") # in some cases there are malformed urls, so extract it
                if path: embed1.set_thumbnail(url=path)
                else: raise ValueError() # URL not found
            except:
                pass # embed1.set_thumbnail(url = 'https://www.airline4.net/assets/img/logos/am_logo.png')

            allianceName = data['user']['alliance']

            value  = f"**​         Rank**: {data['user']['rank']}\n"
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
            embed1.add_field(name='Basic Statistics', inline=False, value=value)
            
            awards = "".join([f"`{strftime('%d/%b/%y', gmtime(award['awarded']))}` - {award['award']}\n" for award in data['awards']])
            if awards:
                embed1.add_field(name=':trophy: Awards', inline=False, value=awards)
            
            if hasIPO:
                x = [i['date'] for i in data['share_development']]
                y = [i['share'] for i in data['share_development']]
                svPerDay = regressionGradient(x, y)*86400
                svValue  = f'**     Average change**: ${svPerDay:,.2f}/day\n'
                svValue += f'**     Estimated Profit**: ${svPerDay*40000000:,.0f}/day\n'
                try:
                    dy = sorted(filter(lambda x:x>0, [y[i]-y[i+1] for i in range(len(y)-1)]))
                    svValue += f"**Estimated Income**: ${40000000*(dy[-1]+dy[-2])/2 / int(data['user']['routes']):,.0f}/flight"
                except:
                    svValue += f"**Estimated Income**: $---/flight"
                embed1.add_field(name='SV details', inline=False, value=svValue)

                await loadingMessage.edit(content='Generating SV graph...')
                graph = discord.File(BytesIO(svgraph(data["share_development"], data['user']['company'])), filename='svGraph.png')
                embed1.set_image(url="attachment://svGraph.png")
                message = await ctx.send(embed=embed1, file=graph)
            else:
                message = await ctx.send(embed=embed1)
            
            await loadingMessage.delete()

            if data['user']['alliance']:
                await message.add_reaction('▶')
        else:
            await ctx.send(f'API Error: {data["status"]["description"]}')
    
    @commands.command(help="Shows an airline's fleet and the total ideal profit", usage='$fleet [optional: airline name/id]', intents = discord.Intents.default())
    @commands.cooldown(200, 86400)
    @notDM()
    @notPriceAlert()
    async def fleet(self, ctx, *, airline = ''):
        global fleetC
        fleetC += 1
        message = await ctx.send('Calculating, Please Wait...\nAccessing the Api...')
        total = 0
        fleet = 0
        bumsecks = 0

        useId = False
        if airline == '': # querying itself
            airline = ctx.author.display_name
            if '%' not in airline: airline = quote(airline)

            s = discordSettings(discordUserId=ctx.author.id).getUserSettings()
            if 'userid' in s:
                userId = s['userid']
                useId = True
        else:
            try:
                userId = int(airline)
                useId = True
            except: # if input airline is not int-able
                if str(airline)[-1] == '>': # is mentioning someone
                    try: 
                        #airline = ctx.guild.get_member(int(airline.replace('<@!', '').replace('>', '')))
                        UID = int(airline.replace('<@!', '').replace('>', ''))
                        s = discordSettings(discordUserId=UID).getUserSettings()
                        if 'userid' in s:
                            userId = s['userid']
                            useId = True
                        else:
                            #airline = airline.display_name
                            await message.edit(content = 'Error:\nCould not find this user. Try entering their nickname instead.')
                            return
                    except:
                        await message.edit(content = 'Error:\nCould not find this user.')
                        return
                airline = airline.replace('<s>', ' ').replace('࣪', ' ') # for space in front of airlines.
                if '%' not in airline: airline = quote(airline)

        url = f'https://www.airline4.net/api/?access_token={AM4token}&id={userId}' if useId else f'https://www.airline4.net/api/?access_token={AM4token}&user={airline}'
        with urlopen(url) as f:
            data = json.load(f)
        if data['status']['request'] == 'success':
            # Logs(username=data['user']['company']).saveInfo(data) # save it for future use.
            if data['user']['game_mode'] == 'Realism':
                mode = 2
            else:
                mode = 5
            embeds = list()
            eCount = 0
            embeds.append(discord.Embed(title = f'Fleet of {data["user"]["company"]}', colour = discord.Colour(0xffee00)))
            #embed.set_footer(text=f"Data updated live from the AM4 API; requests remaining: {data['status']['requests_remaining']}\nData and Profit Formula provided by Scuderia Airlines' AC database.\nSupport us by donating! For more info, use the $donate command.")
            await message.edit(content = 'Calculating, Please Wait...\nEstablishing connection to the Database')
            conn = await aiomysql.connect(user='***REMOVED***',
                                        password='***REMOVED***',
                                        host='***REMOVED***',
                                        db='***REMOVED***')
            acn = 0
            bar = ''
            for fleet in data['fleet']: bar += '▯'
            for fleet in data['fleet']:
                acn += 1
                await message.edit(content = f'Calculating, Please Wait...\nCalculating Profit: {acn}/{len(data["fleet"])}\n{bar}')
                bar = IncrementBar(bar)
                succ = False
                ac = fleet['aircraft']
                cursor = await conn.cursor()
                await cursor.execute(f"SELECT `manf`, `aircraft`, `rng`, `co2`, `fuel`, `spd`, `cap`, `model`, `cost`, `img`, `type` FROM `am4bot` WHERE `model` = '{ac}'")
                plane = await cursor.fetchone()
                if plane: succ = True
                if not plane:
                    embeds[eCount].add_field(name = 'Plane:', value = f'**{ac}** x {fleet["amount"]}', inline = False)
                else:
                    if plane[10] == 'Pax':
                        pro = profit(plane)
                    else:
                        pro = procargo(plane)
                    ac = plane[1]
                    total += pro[mode]*fleet["amount"] 
                    embeds[eCount].add_field(name = 'Plane:', value = f'**{ac}** x {fleet["amount"]} | Max Profit: **${pro[mode]*fleet["amount"]:,}**', inline = False)
                if len(embeds[eCount].fields) == 25:
                    eCount += 1
                    embeds.append(discord.Embed(colour = discord.Colour(0xffee00)))
                if len(embeds) == 10:
                    await ctx.send("You've done it, you crazy son of a bitch, you've reached Discord's limits. I cannot display your entire fleet. Congratulations. Now go on, do something useful with your life. Find a new hobby. Learn a new skill. Touch grass. Find new friends. Go, my child, you're free now.")
                bumsecks += fleet['amount']
            embeds[eCount].add_field(name = 'Fleet', value = f"Total Planes: **{bumsecks}**")
            embeds[eCount].add_field(name = 'Profit', value = f"Total Ideal Profit per Day: **${total:,}**" + ("\*" if not succ else ""))
            embeds[eCount].set_footer(text=f"Data updated live from the AM4 API; requests remaining: {data['status']['requests_remaining']}\nData and Profit Formula provided by Scuderia Airlines' AC database.\nSupport us by donating! For more info, use the $donate command.")

            await message.delete()
            for mbed in embeds:
                await ctx.send(content = '', embed = mbed)
            await cursor.close()
            conn.close()
        else:
            await message.edit(content = f'API Error: {data["status"]["description"]}')

    '''
    GuideDev use:
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    $reloadSVgraphCode
    '''

    @commands.command(hidden=True)
    @guideDevsOnly()
    async def reloadSVgraphCode(self, ctx):
        importlib.reload(graphgen)
        await ctx.send('SV graph code updated.')

def setup(bot):
    bot.add_cog(AM4APICog(bot))
