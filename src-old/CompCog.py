info = 'Poster Competition Extension v1.1'

import discord
from discord.ext import commands
import csv
import json
from checks import *

running = False
players = None

class CompCog(commands.Cog, name = 'Poster Competition Commands'):
    def __init__(self, bot):
        global players, data
        self.bot = bot
        with open("CompetitionData.json", "r") as f:
            data = json.load(f)
            players = list(data.keys())
        try: self.bot.competitioninfo = data["info"]
        except: pass
        print(f'Loaded {info}!')

    '''
    Public use:
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    $comp|competition
    $comp submit
    '''

    @commands.group(aliases = ['comp'])
    @notDM()
    @notPriceAlert()
    async def competition(self, ctx):
        if ctx.invoked_subcommand == None:
            await ctx.send(self.bot.competitioninfo)
    
    @competition.command()
    @notDM()
    @notPriceAlert()
    async def submit(self, ctx, link = None):
        global players, data
        if running:
            if ctx.message.author.display_name not in players:
                if link == None and ctx.message.attachments == None:
                    await ctx.send('No file found.')
                else:
                    if link == None and ctx.message.attachments[0]:
                        link = f"{ctx.message.attachments[0].url}"
                    submissions = csv.writer(open("submissions.csv", 'a'), lineterminator = '\n')
                    submissions.writerow([ctx.message.author.display_name, link])
                    players.append(ctx.message.author.display_name)
                    data[ctx.message.author.display_name] = "submitted"
                    with open("CompetitionData.json", "w") as f:
                        json.dump(data, f)
                    await ctx.send("Thank you. Your submission has been sent.")
            else: await ctx.send("You can't submit twice!\nIf you feel this is wrong, contact a mod.")
        else: await ctx.send("Competition currently not running!")

    '''
    GuideDev use:
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    $comp start
    $comp stop
    $comp setinfo
    $comp reset
    '''

    @competition.command()
    @guideDevsOnly()
    async def start(self, ctx):
        global running
        running = True
        await ctx.send('Competition started.')
    
    @competition.command()
    @guideDevsOnly()
    async def stop(self, ctx):
        global running
        running = False
        await ctx.send('Competition stopped.')
    
    @competition.command()
    @guideDevsOnly()
    async def setinfo(self, ctx, reee):
        global players
        del players
        players = list()
        data['info'] = self.bot.competitioninfo = reee
        with open("CompetitionData.json", "w") as f:
            json.dump(data, f)
        await ctx.send('Competition information set.')
    
    @competition.command()
    @guideDevsOnly()
    async def reset(self, ctx):
        global players
        del players
        players = list()
        data['info'] = self.bot.competitioninfo
        with open("CompetitionData.json", "w") as f:
            json.dump(data, f)
        await ctx.send('Competition resetted.')
        
def setup(bot):
    bot.add_cog(CompCog(bot))
