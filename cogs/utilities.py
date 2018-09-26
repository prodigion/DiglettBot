import discord
from discord.ext import commands

"""Utility functions"""

class UtilityCog:
    """UtilityCog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='me')
    @commands.is_owner()
    async def only_me(self, ctx):
        """A simple command which only responds to the owner of the bot."""

        await ctx.send(f'Hello {ctx.author.mention}. This command can only be used by you!!')

    @commands.command(name='coolbot')
    async def cool_bot(self, ctx):
        """Is the bot cool?"""
        await ctx.send('This bot is cool. :)')

    @commands.command(name='nests')
    @commands.guild_only()
    async def print_nests(self, ctx):
        """Print nests"""

        if ctx.channel.id == 328348774285967362:
          await ctx.send(f'Reposting NestDoc links; see below...\n\nhttps://goo.gl/jRvJWH (Active nests)\nhttps://goo.gl/hQ5B7B (Submit nesting Pokemon)')

        await ctx.message.delete()

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(UtilityCog(bot))
