from discord.ext.commands import check, has_role
from discord.utils import get
import discord
import glob
import random

def guideDevsOnly():
    async def predicate(ctx):
        try:
            role = get(ctx.author.roles, id=646148607636144131)
            if role is None:
                await ctx.send("You do not have the required roles to use this command.")
                return False
        except:
            return False
        return True
    return check(predicate)

def modsOnly():
    async def predicate(ctx):
        try:
            modRole = get(ctx.author.roles, id=514431344764256276)
            helperRole = get(ctx.author.roles, id=931616311358939227)
            if modRole is None and helperRole is None:
                await ctx.send("You do not have the required roles to use this command.")
                return False
        except:
            return False
        return True
    return check(predicate)

def modsOrStars():
    async def predicate(ctx):
        try:
            modRole = get(ctx.author.roles, id=514431344764256276)
            starRole = get(ctx.author.roles, id=701410528853098497)
            if modRole is None and starRole is None:
                await ctx.send("You do not have the required roles to use this command.")
                return False
        except:
            return False
        return True
    return check(predicate)

def notPriceAlert():
    async def predicate(ctx):
        try:
            if ctx.message.channel.id == 554503485765189642:
                await ctx.send(f'This command is disabled here. Please go to <#475885102178631680>.')
                return False
            elif ctx.message.channel.id not in [
                475885102178631680,
                659878639461990401,
                789477232900833290,
                701324942943191110,
                475629813831565312,
            ]:
                imgName = random.choice(glob.glob("data/notbotspam/*"))
                messages = await ctx.message.channel.history(limit=2).flatten()
                if messages[1].content != '$ignore':
                    with open(imgName, 'rb') as fp:
                        await ctx.message.channel.send(file=discord.File(fp, filename='botspampls.png'))
                    return False
        except Exception as e:
            print(e)
            return True
        return True
    return check(predicate)

def notDM():
    async def predicate(ctx):
        if ctx.guild is None and ctx.message.author.id != 668261593502580787:
            await ctx.send("Commands are disabled within DMs.")
            return False
        return True
    return check(predicate)

def isPositiveInteger(x):
    try:
        x = int(x)
        if x > 0:
            return True
        else:
            return False
    except:
        return False