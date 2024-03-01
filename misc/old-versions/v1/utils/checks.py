from discord.ext.commands import check, has_role
from discord.utils import get

def guideDevsOnly():
    async def predicate(ctx):
        role = get(ctx.author.roles, id=646148607636144131)
        if role is None:
            await ctx.send("You do not have the required roles to use this command.")
            return False
        return True
    return check(predicate)

def modsOnly():
    async def predicate(ctx):
        role = get(ctx.author.roles, id=514431344764256276)
        if role is None:
            await ctx.send("You do not have the required roles to use this command.")
            return False
        return True
    return check(predicate)

def notPriceAlert():
    async def predicate(ctx):
        if ctx.message.channel.id == 733532746416259083:
            await ctx.send(f'This command is disabled here. Please go to <#475885102178631680>.')
            return False
        return True
    return check(predicate)

def notDM():
    async def predicate(ctx):
        if ctx.guild is None:
            await ctx.send("Commands are disabled within DMs.")
            return False
        return True
    return check(predicate)