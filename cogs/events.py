import discord
from discord.ext import commands
import aiomysql

class EventsCog:
    """EventsCog"""

    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

        print(f'\n\nLogged in as: {self.bot.user.name} - {self.bot.user.id}\nVersion: {discord.__version__}\n')

        # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
        await self.bot.change_presence(activity=discord.Game(name='Pokemon Go', type=1))
        self.bot.pool = await aiomysql.create_pool(host=self.bot.configs['host'], port=self.bot.configs['port'],
                                                   user=self.bot.configs['user'], password=self.bot.configs['pass'],
                                                   db=self.bot.configs['db'])
        print(f'Successfully logged in and booted...!')

    async def on_message(self, message: discord.Message):
        for mention in message.role_mentions:
          if mention.name in ["rh0", "rh1", "rh2", "rh3", "rh4", "rh5", "rh6", "rh7", "rh8", "rh9", "hundo"]:
            roleChannel = discord.utils.get(message.guild.channels, name="role-select")
            await message.channel.send(f"To get tagged when someone mentions `@{mention.name}`, please go to {roleChannel.mention} and type `!{mention.name}`.")

def setup(bot):
    bot.add_cog(EventsCog(bot))