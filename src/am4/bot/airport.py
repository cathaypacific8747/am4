from discord.ext import commands


class AirportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="finds an airport")
    async def airport(self, ctx: commands.Context):
        await ctx.send("test")
