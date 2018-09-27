import discord
from discord.ext import commands

class EventsCog:
    """EventsCog"""

    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

        print(f'\n\nLogged in as: {self.bot.user.name} - {self.bot.user.id}\nVersion: {discord.__version__}\n')

        # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
        await self.bot.change_presence(activity=discord.Game(name='Pokemon Go', type=1))
        print(f'Successfully logged in and booted...!')

def setup(bot):
    bot.add_cog(EventsCog(bot))
