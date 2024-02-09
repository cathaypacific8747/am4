from am4.utils import __version__ as am4utils_version
from discord.ext import commands
from discord.mentions import AllowedMentions


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="shows information about our bot")
    async def botinfo(self, ctx: commands.Context):
        await ctx.send(
            (
                f"**AM4 ACDB Bot** (`.utils`: v{am4utils_version})\n"
                "Made by <@697804580456759397> and <@243007616714801157>\n"
                "Database and profit formula by <@663796476257763370>\n"
                "Join our main server: https://discord.gg/4tVQHtf\n"
            ),
            allowed_mentions=AllowedMentions.none(),
        )
