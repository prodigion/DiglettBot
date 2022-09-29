import discord
from discord.ext import commands


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.configs = {}
        self.bot.pool = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

        self.bot.get_cog("ConfigsCog").loadConfigs()
        self.bot.get_cog("ConfigsCog").loadData()

        print(f'\nLogged in as: {self.bot.user.name} - {self.bot.user.id}\nVersion: {discord.__version__}\n')

        # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
        await self.bot.change_presence(activity=discord.Game(name='Pokemon Go', type=1))

        print(f'Successfully logged in and booted...!')

        for guild in self.bot.guilds:
            if str(guild.id) not in self.bot.configs:
                self.bot.configs[str(guild.id)] = dict()
                self.bot.configs[str(guild.id)]['cities'] = dict()
                self.bot.get_cog("ConfigsCog").saveConfigs()
            try:
                await self.bot.get_cog("ResearchCog").connectDB(guild)
            except:
                pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if str(guild.id) not in self.bot.configs:
            self.bot.configs[str(guild.id)] = dict()
            self.bot.get_cog("ConfigsCog").saveConfigs()
        try:
            await self.bot.get_cog("ResearchCog").connectDB(guild)
        except:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        for mention in message.role_mentions:
            if mention.name in ["rh0", "rh1", "rh2", "rh3", "rh4", "rh5", "rh6", "rh7", "rh8", "rh9", "hundo", "nundo"]:
                roleChannel = discord.utils.get(message.guild.channels, name="role-select")
                await message.channel.send(f"To get tagged when someone mentions `@{mention.name}`, please go to {roleChannel.mention} and type `!{mention.name}`.")

        if message.channel.id == self.bot.configs[str(message.guild.id)]['friend-channel']:
            if message.author.id == self.bot.user.id:
                return
            await message.delete()


async def setup(bot):
    await bot.add_cog(EventsCog(bot))
