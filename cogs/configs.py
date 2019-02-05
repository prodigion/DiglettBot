import discord
from discord.ext import commands
from asyncio import TimeoutError
import json

class ConfigsCog:
    """ConfigsCog"""

    def __init__(self, bot):
        self.bot = bot

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
        print("Configuration saved")

    @commands.command(name='diglett')
    @commands.is_owner()
    async def run_config(self, ctx, *, config = ""):
        def check(msg):
            return msg.content != "cancel" and msg.author == ctx.author and msg.channel == ctx.channel

        if config == "":
            await ctx.send("Configuration options: ```nests - Response to !nests command\n" \
                                                     "admins - Assign role with admin access to DiglettBot\n" \
                                                     "team - Channel for team selection\n" \
                                                     "role - Channel for role selection\n" \
                                                     "research - Channel for quest queries```")
        elif config == "nests":
            try:
                await ctx.send("Please enter a response for the `!nests` command. Enter `cancel` to exit.")
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                if msg:
                    pass
                    self.bot.configs[str(ctx.guild.id)]['nests'] = msg.content
                    self.saveConfigs()
            except TimeoutError:
                await ctx.send("Timeout. Role not updated")
        elif config == "admins":
            try:
                await ctx.send("Please enter a role name.  Enter `cancel` to exit.")
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                role = discord.utils.get(ctx.guild.roles, name=msg.content)
                if role:
                    self.bot.configs[str(ctx.guild.id)]['admin-role'] = role.id
                    self.saveConfigs()
            except TimeoutError:
                await ctx.send("Timeout. Role not updated")
            except Exception as e:
                await ctx.send("Error. Role not updated")
                print(e)
        elif config == "team":
            self.bot.configs[str(ctx.guild.id)]['team-channel'] = ctx.channel.id
            self.saveConfigs()
        elif config == "role":
            self.bot.configs[str(ctx.guild.id)]['role-channel'] = ctx.channel.id
            self.saveConfigs()
        elif config == "research":
            self.bot.configs[str(ctx.guild.id)]['research-channel'] = ctx.channel.id
            self.saveConfigs()

        await ctx.message.delete()

    @commands.command(name='dugtrio')
    @commands.is_owner()
    async def run_config_owner(self, ctx, *, config):
        if config == "data load":
            self.loadData()
            await ctx.send("Data load complete")
        elif config == "config save":
            self.saveConfigs()
            await ctx.send("Config saved")
        elif config == "config load":
            self.loadConfigs()
            await ctx.send("Config loaded")

        await ctx.message.delete()

def setup(bot):
    bot.add_cog(ConfigsCog(bot))
