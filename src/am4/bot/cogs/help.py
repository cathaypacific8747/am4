import discord
from am4.utils import __version__ as am4utils_version
from discord.ext import commands
from discord.mentions import AllowedMentions

from ...config import cfg
from ..base import BaseCog
from ..utils import COLOUR_ERROR, COLOUR_GENERIC


class HelpCog(BaseCog):
    @commands.command(brief="Shows information about our bot", ignore_extra=False)
    async def botinfo(self, ctx: commands.Context):
        await ctx.send(
            (
                "# AM4Help.com discord bot\n"
                f"- coreutils version: `{am4utils_version}`\n"
                "- Made by <@697804580456759397>, <@243007616714801157> and <@663796476257763370>\n"
                "- If you need any help, feel free to ask on our support server: https://discord.gg/4tVQHtf\n"
                "- The code is open-source on GitHub at https://github.com/cathaypacific8747/am4 - "
                "feel free to open an issue and/or PR!"
            ),
            allowed_mentions=AllowedMentions.none(),
        )

    @staticmethod
    def _collect_commands_descs(cmd: commands.Command | commands.Group, level=0):
        if not cmd.hidden and cmd.enabled:
            cmd_display = f"{cfg.bot.COMMAND_PREFIX if level == 0 else ''}{'  ' * level}{cmd.name}"
            desc = f"`{cmd_display:<10}`{'  ' * level} - {cmd.short_doc}\n"
            if isinstance(cmd, commands.Group):
                desc += "".join(HelpCog._collect_commands_descs(subcmd, level + 1) for subcmd in cmd.commands)
            return desc
        return ""

    @commands.command(brief="Shows this command", ignore_extra=False)
    @commands.guild_only()
    async def help(
        self,
        ctx: commands.Context,
        command: str | None = commands.parameter(default=None, description="Name of the command to show help for"),
        *subcommands: str,
    ):
        if command is None:
            embed = discord.Embed(title="List of commands", colour=COLOUR_GENERIC)
            desc = "".join(HelpCog._collect_commands_descs(cmd) for cmd in self.bot.commands)
            embed.description = desc
            embed.add_field(
                name="Learn more about how to use a command with `$help <cmd>`.",
                value="For example, try:```php\n$help airport\n$help settings show```",
            )
            await ctx.send(embed=embed)
            return

        cmd = self.bot.get_command(command)
        if cmd is None:
            await ctx.send(
                embed=discord.Embed(
                    title="Command does not exist!",
                    description="To show all commands, use `$help`.",
                    colour=COLOUR_ERROR,
                )
            )
        for sc in subcommands:
            cmd = cmd.get_command(sc)
            if cmd is None:
                await ctx.send(
                    embed=discord.Embed(
                        title=f"Subcommand `{sc}` does not exist!",
                        description=f"To show all possible subcommands, use `$help {command}`.",
                        colour=COLOUR_ERROR,
                    )
                )
                return

        embed = discord.Embed(
            title=f"`{cfg.bot.COMMAND_PREFIX}{cmd.qualified_name} {cmd.signature}`", colour=COLOUR_GENERIC
        )
        for p in cmd.clean_params.values():
            name = ":small_blue_diamond: `{}` (Optional)" if not p.required else ":small_orange_diamond: `{}`"
            embed.add_field(
                name=name.format(p.name),
                value=d if (d := p.description) is not None else "",
                inline=True,
            )
        if h := cmd.help or cmd.brief:
            embed.add_field(name="Details", value=h, inline=False)
        await ctx.send(embed=embed)
