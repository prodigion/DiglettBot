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

#    async def on_member_join(self, member: discord.Member):
#        """https://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_member_join"""
#
#        message = f"Welcome to PokeOntario, {member.mention}! Set your team by typing `!mystic`, `!valor`, `!instinct` or `!harmony`. If you have any questions tag the `@Mods`."
#        await self.bot.get_channel(259766286546894849).send(message)

def setup(bot):
    bot.add_cog(EventsCog(bot))
