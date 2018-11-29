import discord
from discord.ext import commands
import json

class ConfigsCog:
    """ConfigsCog"""

    def __init__(self, bot):
        self.bot = bot
        with open('config.json', 'r') as f:
            self.bot.configs = json.load(f)

def setup(bot):
    bot.add_cog(ConfigsCog(bot))
