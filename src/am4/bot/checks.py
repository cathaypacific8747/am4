from discord.ext.commands import Context, check
from discord.utils import get

from ..config import Config


def guideDevsOnly():
    async def predicate(ctx: Context):
        try:
            role = get(ctx.author.roles, id=646148607636144131)
            if role is None:
                await ctx.send(
                    "You do not have the required roles to use this command."
                )
                return False
        except Exception:
            return False
        return True

    return check(predicate)


def modsOnly():
    async def predicate(ctx: Context):
        try:
            modRole = get(ctx.author.roles, id=Config.MODERATOR_ROLEID)
            helperRole = get(ctx.author.roles, id=Config.HELPER_ROLEID)
            print(modRole, helperRole)
            if modRole is None and helperRole is None:
                await ctx.send(
                    "You do not have the required roles to use this command."
                )
                return False
        except Exception:
            return False
        return True

    return check(predicate)


def modsOrStars():
    async def predicate(ctx: Context):
        try:
            modRole = get(ctx.author.roles, id=Config.MODERATOR_ROLEID)
            starRole = get(ctx.author.roles, id=701410528853098497)
            if modRole is None and starRole is None:
                await ctx.send(
                    "You do not have the required roles to use this command."
                )
                return False
        except Exception:
            return False
        return True

    return check(predicate)


def ignore_pricealert():
    async def predicate(ctx: Context):
        try:
            if ctx.message.channel.id == Config.PRICEALERT_CHANNELID:
                await ctx.send(
                    f"This command is disabled here. Please go to <#{Config.BOTSPAM_CHANNELID}>."
                )
                return False
        except Exception as e:
            print(e)
            return True
        return True

    return check(predicate)


def ignore_dm():
    async def predicate(ctx: Context):
        if ctx.guild is None:  # and ctx.message.author.id != 668261593502580787:
            await ctx.send("Commands are disabled within DMs.")
            return False
        return True

    return check(predicate)


def isPositiveInteger(x):
    try:
        return int(x) > 0
    except Exception:
        return False
