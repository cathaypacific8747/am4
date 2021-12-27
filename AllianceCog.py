info = 'Alliances Cog v1.0'

import discord
from discord.ext import commands
import urllib3
import json
from graphgen import *
from io import BytesIO
from checks import *
from urllib.parse import quote
import time

token = '***REMOVED***'

class AlliancesCog(commands.Cog, name = 'Alliance Commands'):
    def __init__(self, bot):
        self.bot = bot
        print(f'Loaded {info}!')

    '''
    All commands here shall be accessible by mods only.
    $watchlist
    $memberCompare
    $alliance
    '''

    @commands.command(hidden=True, usage='$watchlist\n$watchlist add|+ <alliance>\n$watchlist remove|rm|- <alliance>', help='Mods-only use.\nViews or edits the current watchlist. Any alliance on the watchlist will have their data requested every hour.\nAffects $allianceCompare.')
    @modsOrStars()
    async def watchlist(self, ctx, *args):
        targetAlliance = " ".join(args[1:])
        if args == ():
            with open('data/watchlist.csv', 'r', newline='') as f:
                allianceList = "\n • ".join(f.read().split(','))
                await ctx.send(f'**Current Watchlist:\n** • {allianceList}')
        elif args[0] == 'add' or args[0] == '+':
            with open('data/watchlist.csv', 'a', newline='') as f:
                f.write(f',{targetAlliance}')
                await ctx.send(f'Successfully added **{targetAlliance}** to the watchlist.')
        elif args[0] == 'remove' or args[0] == 'rm' or args[0] == '-':
            with open('data/watchlist.csv', 'r+', newline='') as f:
                currentWatchList = f.read().split(',')
                if targetAlliance in currentWatchList:
                    currentWatchList.remove(targetAlliance)
                    f.seek(0)
                    f.write(','.join(currentWatchList))
                    f.truncate()
                    await ctx.send(f'**{targetAlliance}** has been removed from the watchlist.')
                else:
                    await ctx.send(f'Cannot find **{targetAlliance}** in the watchlist.')

    @commands.command(hidden=True, usage='$memberCompare <alliance1> <alliance2>', help="Mods-only use. Both arguments required.\nReturns two graphs: descending contribution, descending share value.\nNote: Each command calls the API twice, so don't call it excessively :)")
    @modsOrStars()
    async def memberCompare(self, ctx, alliance1, alliance2):
        http = urllib3.PoolManager()
        loadingMessage = await ctx.send(f"Requesting *{alliance1}*'s data.")
        allianceData1 = json.loads(http.request('GET', f'https://www.airline4.net/api?access_token={token}&search={quote(alliance1)}').data.decode('utf-8'))

        await loadingMessage.edit(content=f"Requesting *{alliance2}*'s data.")
        allianceData2 = json.loads(http.request('GET', f'https://www.airline4.net/api?access_token={token}&search={quote(alliance2)}').data.decode('utf-8'))

        if allianceData1['status']['request'] != 'success' or allianceData2['status']['request'] != 'success':
            await loadingMessage.edit(content=':x: An error occured. Please check inputs.')
        else:
            await loadingMessage.edit(content='Generating contribution graph...')
            contributionGraph = discord.File(BytesIO(allianceMemberGraph(allianceData1, allianceData2, 'contrib')), filename='allianceGraph.png')
            await loadingMessage.edit(content='Generating share value graph...')
            shareValueGraph = discord.File(BytesIO(allianceMemberGraph(allianceData1, allianceData2, 'shareValue')), filename='allianceGraph.png')
            await loadingMessage.edit(content='Sending files...')
            await ctx.send(file=contributionGraph)
            await ctx.send(file=shareValueGraph)
            await loadingMessage.delete()

    @commands.command(hidden=True, usage='$alliance <alliance>', help='Mods-only use.\nShows the A.V. progression graph of a specified alliance over time. Also shows the rate of A.V. change over time.\nAlliance specified must be added to the watchlist.')
    @modsOrStars()
    async def alliance(self, ctx, *targetAlliance):
        allianceName = " ".join(targetAlliance)
        try:
            with open('data/log/allianceLog.json') as f:
                loadingMessage = await ctx.send('Searching logs...')
                data = json.load(f)
                if allianceName in data:
                    await loadingMessage.edit(content='Generating SV progression graph...')
                    try:
                        svProgression = discord.File(BytesIO(svProgressionGraph(data[allianceName])), filename='svProgressionGraph.png')
                        await loadingMessage.edit(content="Generating bottom 5 performers' historic contributions graph...")
                        historicContrib = discord.File(BytesIO(historicContribGraph(data[allianceName])), filename='svProgressionGraph.png')
                        await ctx.send(file=svProgression)
                        await ctx.send(file=historicContrib)
                        await loadingMessage.delete()
                    except:
                        await loadingMessage.edit(content=f':x: Graph generation error. Please wait at least 2 hours and try again.')
                else:
                    await loadingMessage.edit(content=f':x: Alliance not recognised in the logs. Use `$watchlist add {allianceName}` and wait for at least 2 hours for the data to populate.')
        except:
            await ctx.send(':x: File read error. Another process is now updating data to the log file. Please wait 1 minute and try again.')

    @commands.command(hidden=True, usage='$allianceCompare <alliance1> <alliance2>', help='Mods-only use.\nShows the A.V. progression graph of the two specified alliance over time. Also shows gap difference between the two.\nBoth alliances specified must be added to the watchlist.')
    @modsOrStars()
    async def allianceCompare(self, ctx, alliance1, alliance2):
        try:
            with open('data/log/allianceLog.json') as f:
                loadingMessage = await ctx.send('Searching logs...')
                data = json.load(f)
                if alliance1 and alliance2 in data:
                    try:
                        await loadingMessage.edit(content=f'Generating A.V. comparison graph...')
                        svComparison = discord.File(BytesIO(svComparisonGraph(data[alliance1], data[alliance2])), filename='svComparisonGraph.png')
                        await ctx.send(file=svComparison)
                        del svComparison

                        await loadingMessage.edit(content=f'Generating contrib. comparison graph...')
                        c = contribGraph(data[alliance1], data[alliance2])
                        contribComparison = discord.File(BytesIO(c), filename='contribGraph.png')
                        await ctx.send(file=contribComparison)
                        del contribComparison
                        
                        await loadingMessage.edit(content=f'Generating 12-hour contrib. comparison graph...')
                        if len(data[alliance1]) > 12 and len(data[alliance2]) > 12:
                            c = actualContribGraph(data[alliance1], data[alliance2])
                            actualContribComparison = discord.File(BytesIO(c), filename='actualContribGraph.png')
                            await ctx.send(file=actualContribComparison)
                        else:
                            await ctx.send(':x: Unable to generate actual contribution difference graph due to the lack of data. Please wait at least 12 hours and try again.')

                        await loadingMessage.delete()
                    except:
                        await loadingMessage.edit(content=f':x: Graph generation error. Please wait at least 2 hours and try again.')
                else:
                    await loadingMessage.edit(content=f':x: Alliance(s) not recognised in the logs. Check the list of alliances with `$watchlist`.')
        except:
            await ctx.send(':x: File read error. Another process is now updating data to the log file. Please wait 1 minute and try again.')

        del alliance1
        del alliance2
        del f
        del loadingMessage
        del data
        del c
        del actualContribComparison
        print(locals().values())

    @commands.command(hidden=True, usage='$member <member1> [member2] [...]', help='Mods-only use.\nShows the contribution/day, contribution and share value history graphs for the specified member(s) within/across tracked alliances.')
    @modsOrStars()
    async def member(self, ctx, *members):
        with open('data/log/allianceLog.json') as f:
            loadingMessage = await ctx.send('Searching logs...')
            try:
                data = json.load(f)
                await loadingMessage.edit(content="Verifying member's data avaliability...")
                memberDetails = {}
                for alliance in data:
                    for timeKey in data[alliance]:
                        for member in data[alliance][timeKey]['members']:
                            memberName = member['company']
                            del member['company']
                            if memberName in members:
                                if memberName not in memberDetails:
                                    memberDetails[memberName] = {timeKey: member}
                                else:
                                    memberDetails[memberName][timeKey] = member
                if not memberDetails:
                    await ctx.send(':x: No such user found. Please check that the names are correct and are in any alliance specified in `$watchlist`.')
                else:
                    try:
                        await loadingMessage.edit(content="Generating contribution/day history graph...")
                        dailyContribHist = discord.File(BytesIO(dailyContribHistGraph(memberDetails, 'dailyContribution')), filename='dailyContribHistGraph.png')
                        await loadingMessage.edit(content="Generating contribution history graph...")
                        contribHist = discord.File(BytesIO(dailyContribHistGraph(memberDetails, 'contributed')), filename='contributedHistGraph.png')
                        await loadingMessage.edit(content="Generating share value history graph...")
                        svHist = discord.File(BytesIO(dailyContribHistGraph(memberDetails, 'shareValue')), filename='svHistGraph.png')
                        await loadingMessage.edit(content="Sending files...")
                        await ctx.send(file=dailyContribHist)
                        await ctx.send(file=contribHist)
                        await ctx.send(file=svHist)
                        await loadingMessage.delete()
                    except:
                        await loadingMessage.edit(content=f':x: Graph generation error. Please wait at least 2 hours for the data to populate and try again.')
            except:
                await ctx.send(':x: File read error. Another process is now updating data to the log file. Please wait 1 minute and try again.')

    @commands.command(hidden=True, usage='$actions <member> [maxResults:100]', help='Mods-only use.\nLists a timeline of estimated departures, contributions and profits.\nBest viewed on Desktop.')
    @modsOrStars()
    async def actions(self, ctx, memberN, maxResults='default'):
        try:
            if maxResults == 'default':
                maxResults = 100
            maxResults = int(maxResults)
        except:
            await ctx.send(':x: `maxResults` is not an integer, setting it to default.')
            maxResults = 100
        try:
            with open('data/log/allianceLog.json') as f:
                loadingMessage = await ctx.send('Searching logs...')
                data = json.load(f)
                await loadingMessage.edit(content="Verifying member's data avaliability...")
                memberDetails = {}
                for alliance in data:
                    for timeKey in data[alliance]:
                        for member in data[alliance][timeKey]['members']:
                            if member['company'] == memberN:
                                memberDetails[timeKey] = member
                if not memberDetails:
                    await loadingMessage.edit(content=':x: No such user found. Please check that the names are correct and are in any alliance specified in `$watchlist`.')
                elif len(memberDetails) == 1:
                    await loadingMessage.edit(content=':x: Not enough data. Please wait for an hour or two for the data to populate.')
                else:
                    oldDetail = list(memberDetails.values())[0]
                    embed = discord.Embed(title=f'Estimated actions of **{memberN}**', colour=0xa3cc00)
                    valuesDict = {
                        'value1': '',
                        'value2': '',
                        'value3': '',
                        'value4': '',
                        'value5': '',
                        'value6': '',
                        'value7': '',
                        'value8': '',
                        'value9': '',
                        'value10': '',
                    }
                    lines = []
                    for i in range(1, len(memberDetails)):
                        detail = memberDetails[list(memberDetails)[i]]
                        dFlights = detail['flights'] - oldDetail['flights']
                        dContrib = detail['contributed'] - oldDetail['contributed']
                        dProfit = (detail['shareValue'] - oldDetail['shareValue']) * 40000000
                        dT = (time.time() - detail['online'])/3600
                        
                        if detail['flights'] != oldDetail['flights']: # departure
                            ind = ':red_circle:' if dProfit < 0 else ':green_circle:'
                            lines.append(f'`{-dT:>7.2f}`h - {ind} **`{dFlights:>3}`dep.** → $`{dContrib:>5}` @ $`{dProfit:>14,.0f}`\n')
                        elif detail['shareValue'] != oldDetail['shareValue']: # unknown
                            ind = ':red_square:' if dProfit < 0 else ':green_square:'
                            lines.append(f'`{-dT:>7.2f}`h - {ind} `                   ` $`{dProfit:>14,.0f}`\n')
                        oldDetail = detail
                        
                    currentValue = 1
                    lines = sorted(lines, key=lambda l: float(l.split('`')[1]))
                    for l in lines[-maxResults:]:
                        if len(valuesDict[f'value{currentValue}']) + len(l) > 1024:
                            currentValue += 1
                        if currentValue == 11:
                            break
                        valuesDict[f'value{currentValue}'] += l

                    ###########################
                    embed1 = discord.Embed(title=f'Log of estimated actions by **{memberN}**', description='Squares = unknown actions (fuel, co2, maintenance),\nCircle = departures.', colour=0x008099)
                    embed2 = discord.Embed(title=f'Continued:', colour=0x008099)

                    count = 1
                    for v in valuesDict:
                        if valuesDict[v]:
                            if count <= 5:
                                embed1.add_field(name='​', value=valuesDict[v], inline=False)
                            else:
                                embed2.add_field(name='​', value=valuesDict[v], inline=False)
                        count += 1
                    await loadingMessage.edit(embed=embed1)
                    if valuesDict['value6']:
                        await ctx.send(embed=embed2)
        except:
            await ctx.send(':x: File read error. Another process is now updating data to the log file. Please wait 1 minute and try again.')

def setup(bot):
    bot.add_cog(AlliancesCog(bot))