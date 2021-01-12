info = 'Settings Cog v1.0'

import discord
from discord.ext import commands
import csv
import json
from checks import *

class discordSettings:
    def __init__(self, discordUserId):
        self.discordUserId = discordUserId
        with open('data/settings/possibleSettings.json', 'r') as f:
            self.allSettings = json.load(f)
        try:
            with open(f'data/settings/{self.discordUserId}.json', 'r') as f:
                self.userSettings = json.load(f)
        except:
            self.userSettings = {}
    
    def getAllSettings(self):
        return self.allSettings
    
    def getUserSettings(self):
        return self.userSettings

    def validateAndFormat(self, value, mode):
        if mode == 0:
            return {'error': None, 'value': value}
        if mode == 1:
            # isInteger
            try:
                v = int(value)
                if v <= 0:
                    raise ValueError()
                return {'error': None, 'value': v}
            except:
                return {'error': f'The value `{value}` must be a positive integer.'}

    def removeSetting(self, settingKey):
        removed = False
        if self.userSettings:
            try:
                with open(f'data/settings/{self.discordUserId}.json', 'r+') as f:
                    settings = json.load(f)
                    k = str(settingKey).lower()
                    if k in settings:
                        v = settings[k]
                        del settings[k]
                        f.seek(0)
                        json.dump(settings, f, indent=4)
                        f.truncate()
                        removed = {
                            'name': k,
                            'value': v
                        }
                    else:
                        removed = None
            except:
                pass
        return removed

    def modifySetting(self, settingKey, newValue):
        modified = False
        for s in self.allSettings:
            if str(settingKey).lower() == s:
                processed = self.validateAndFormat(str(newValue), int(self.allSettings[s]['validationMode']))
                if not processed['error']:
                    self.userSettings[str(settingKey).lower()] = processed['value']
                    with open(f'data/settings/{self.discordUserId}.json', 'w+') as f: # creates new file if entry does not exist
                        json.dump(self.userSettings, f, indent=4)
                        modified = True
                else:
                    modified = processed['error']
                break
        return modified

class CompCog(commands.Cog, name = 'Settings Commands'):
    def __init__(self, bot):
        self.bot = bot
        print(f'Loaded {info}!')

    @commands.command(hidden=True, help='UNDER DEVELOPMENT! Edits user settings.', usage='$settings - shows a list of all possible settings\n$settings <name> - removes the setting with the specified name.\n$settings <name> <value> - adds the setting with the specified name and value.')
    async def settings(self, ctx, *args):
        '''
        $settings             - possible settings
        $settings userId      - wipes that setting
        $settings userId 1234 - sets the setting to the specified value
        '''
        thisUserId = ctx.author.id
        if len(args) == 0:
            embed = discord.Embed(title=f'Settings for **{ctx.author.display_name}**', colour=0xa3cc00)

            settings = discordSettings(discordUserId=thisUserId)
            allSettings = settings.getAllSettings()
            possibleSettings = '\n'.join([f":small_blue_diamond:__**{sName}**__: {allSettings[sName]['description']}" for sName in allSettings])
            
            userSettings = settings.getUserSettings()
            if userSettings:
                currentSettings = '\n'.join([f":small_orange_diamond:**{sName}**: {userSettings[sName]}" for sName in userSettings])
            else:
                currentSettings = '*No settings found.*'

            embed.add_field(name='Possible Settings', value=possibleSettings, inline=False)
            embed.add_field(name='Current Settings', value=currentSettings, inline=False)
            await ctx.send(embed=embed)
        elif len(args) == 1:
            settings = discordSettings(discordUserId=thisUserId)
            removed = settings.removeSetting(args[0])

            if removed == False:            
                embed = discord.Embed(title=f':x: You do not have any settings to be removed.', description='To view a list of settings, use `$settings`.', colour=0xdd2e44)
            elif removed == None:
                embed = discord.Embed(title=f':x: The setting `{args[0]}` cannot be removed because it does not exist.', description=f'Avaliable settings to remove: `{"`,`".join(list(settings.getUserSettings()))}`\nFor more info, use `$settings`.', colour=0xdd2e44)
            else:
                embed = discord.Embed(title=f'<:success:714315538821677118> The setting `{removed["name"]}` with the value of `{removed["value"]}` has been removed.', description=f'To add it back, use `$settings {removed["name"]} {removed["value"]}`.', colour=0xa3cc00)
            await ctx.send(embed=embed)
        elif len(args) == 2:
            settings = discordSettings(discordUserId=thisUserId)
            modified = settings.modifySetting(args[0], args[1])
            if modified == True:
                embed = discord.Embed(title=f'<:success:714315538821677118> The setting `{args[0]}` has been updated to the value of `{args[1]}`.', description=f'To remove this setting, use `$settings {args[0]}`.', colour=0xa3cc00)
            elif modified == False:
                embed = discord.Embed(title=f':x: `{args[0]}` is not a valid setting name.', description='To view a list of possible settings to add, use `$settings`.', colour=0xdd2e44)
            else:
                embed = discord.Embed(title=f':x: Formatting error. {modified}', description='For more information, use `$settings.`', colour=0xdd2e44)
            await ctx.send(embed=embed)
        else: 
            embed = discord.Embed(title=f':x: Too many arguments!', description='Please check `$help settings`', colour=0xdd2e44)
            await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(CompCog(bot))
