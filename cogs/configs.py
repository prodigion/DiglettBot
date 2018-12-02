import discord
from discord.ext import commands
import json

class ConfigsCog:
    """ConfigsCog"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.config = {}
        self.loadConfigs()

    def loadConfigs(self):
        with open('configs.json', 'r') as f:
            self.bot.configs = json.load(f)

    def saveConfigs(self):
        with open('configs.json', 'w') as outfile:
            json.dump(self.bot.configs, outfile, indent=4)

    @commands.command(name='configload')
    @commands.is_owner()
    async def load_config(self, ctx):
        self.loadConfigs()

    @commands.command(name='configsave')
    @commands.is_owner()
    async def write_configs(self, ctx):
        self.saveConfigs()

    @commands.command(name='confignests')
    @commands.is_owner()
    async def setNests(self, ctx, *, msg):
        self.bot.configs[str(ctx.guild.id)]['nests'] = msg
        self.saveConfigs()

def setup(bot):
    bot.add_cog(ConfigsCog(bot))
