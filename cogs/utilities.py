from discord.ext import commands


class UtilityCog(commands.Cog):
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

    @commands.command(name='say', aliases=['copy', 'mimic'])
    @commands.is_owner()
    async def do_say(self, ctx, *, comment: str):
        """A simple command which repeats our input."""

        await ctx.message.delete()
        await ctx.send(comment)

    @commands.command(name='nests')
    @commands.guild_only()
    async def print_nests(self, ctx):
        """Print nests"""

        if ctx.channel.name == "migration-chat":
            await ctx.send(self.bot.configs[str(ctx.guild.id)]['nests'])

        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
