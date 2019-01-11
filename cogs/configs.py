import discord
from discord.ext import commands
import json

class ConfigsCog:
    """ConfigsCog"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.configs = {}
        self.loadConfigs()
        self.loadData()

    def loadData(self):
        with open('i18n/en.json', 'r') as f:
            self.bot.data = json.load(f)

        for data in ('pokedex', 'items', 'pokemon_types', 'activities'):
            self.bot.data[data] = {int(k):v for k,v in self.bot.data[data].items()}

        for data in ('types', 'conditions'):
            self.bot.data['quests'][data] = {int(k):v for k,v in self.bot.data['quests'][data].items()}
        print("Data loaded")

    def loadConfigs(self):
        with open('configs.json', 'r') as f:
            self.bot.configs = json.load(f)
        print("Configuration loaded")

    def saveConfigs(self):
        with open('configs.json', 'w') as outfile:
            json.dump(self.bot.configs, outfile, indent=4)
        print("Config SAVED")

    @commands.command(name='dataload')
    @commands.is_owner()
    async def load_data(self, ctx):
        self.loadData()
        await ctx.message.delete()

    @commands.command(name='configload')
    @commands.is_owner()
    async def load_config(self, ctx):
        self.loadConfigs()
        await ctx.message.delete()

    @commands.command(name='configsave')
    @commands.is_owner()
    async def write_configs(self, ctx):
        self.saveConfigs()
        await ctx.message.delete()

    @commands.command(name='confignests')
    @commands.is_owner()
    async def setNests(self, ctx, *, msg):
        self.bot.configs[str(ctx.guild.id)]['nests'] = msg
        self.saveConfigs()

def setup(bot):
    bot.add_cog(ConfigsCog(bot))
