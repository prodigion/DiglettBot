import discord
from discord.ext import commands
from asyncio import TimeoutError
import json


class ConfigsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def loadData(self):
        with open('i18n/en.json', 'r') as f:
            self.bot.data = json.load(f)

        for data in ('pokedex', 'items', 'pokemon_types', 'activities'):
            self.bot.data[data] = {int(k): v for k, v in self.bot.data[data].items()}

        for data in ('types', 'conditions'):
            self.bot.data['quests'][data] = {int(k): v for k, v in self.bot.data['quests'][data].items()}
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
    async def run_config(self, ctx, *, config=""):
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        if config == "":
            await ctx.send("Configuration options: ```nests - Response to !nests command\n"
                                                    "map info - Details about mapping data source\n"
                                                    "admins - Assign role with admin access to DiglettBot\n"
                                                    "team - Channel for team selection\n"
                                                    "role - Channel for role selection\n"
                                                    "friend - Channel for friend code listing\n"
                                                    "research - Channel for quest queries```")
        elif config == "nests":
            try:
                await ctx.send("Please enter a response for the `!nests` command. Enter `cancel` to exit.")
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                if msg:
                    if msg.content == "cancel":
                        await ctx.send("Cancelled")
                        return
                    self.bot.configs[str(ctx.guild.id)]['nests'] = msg.content
                    self.saveConfigs()
                    await ctx.send("Nests command updated")
            except TimeoutError:
                await ctx.send("Timeout. Role not updated")
        elif config == "map info":
            try:
                await ctx.send("Please enter the map information. Enter `cancel` to exit.")
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                if msg:
                    if msg.content == "cancel":
                        await ctx.send("Cancelled")
                        return
                    self.bot.configs[str(ctx.guild.id)]['map-info'] = msg.content
                    self.saveConfigs()
                    await ctx.send("Map info updated")
            except TimeoutError:
                await ctx.send("Timeout. Map info not updated")
            except Exception as e:
                await ctx.send("Error. Map info not updated")
                print(e)
        elif config == "admins":
            try:
                await ctx.send("Please enter a role name.  Enter `cancel` to exit.")
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                if msg:
                    if msg.content == "cancel":
                        await ctx.send("Cancelled")
                        return
                    role = discord.utils.get(ctx.guild.roles, name=msg.content)
                    self.bot.configs[str(ctx.guild.id)]['admin-role'] = role.id
                    self.saveConfigs()
                    await ctx.send("Admin role updated")
            except TimeoutError:
                await ctx.send("Timeout. Role not updated")
            except Exception as e:
                await ctx.send("Error. Role not updated")
                print(e)
        elif config == "team":
            self.bot.configs[str(ctx.guild.id)]['team-channel'] = ctx.channel.id
            self.saveConfigs()
            await ctx.send("Team selection channel updated")
        elif config == "role":
            self.bot.configs[str(ctx.guild.id)]['role-channel'] = ctx.channel.id
            self.saveConfigs()
            await ctx.send("Role selection channel updated")
        elif config == "friend":
            self.bot.configs[str(ctx.guild.id)]['friend-channel'] = ctx.channel.id
            self.saveConfigs()
            await ctx.send("Friend code reporting channel updated")
        elif config == "research":
            try:
                await ctx.send("Please enter a city name.  Enter `delete` to de-register this channel. Enter `cancel` to exit.")
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                if msg:
                    if msg.content == "cancel":
                        await ctx.send("Cancelled")
                        return
                    if msg.content == "delete":
                        city = self.bot.configs[str(ctx.guild.id)]['cities'].pop(str(ctx.channel.id))
                        await ctx.send(city['city'] + " deleted")
                        self.saveConfigs()
                        return
                    cityName = msg.content
                    await ctx.send("City: " + cityName)

                await ctx.send("Please enter a geofence.  Enter `cancel` to exit.")
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                if msg:
                    if msg.content == "cancel":
                        await ctx.send("Cancelled")
                        return
                    geofence = msg.content
            except TimeoutError:
                await ctx.send("Timeout. City not updated")
            except Exception as e:
                await ctx.send("Error. City not updated")
                print(e)
            city = {
                "city": cityName,
                "geofence": geofence
            }
            self.bot.configs[str(ctx.guild.id)]['cities'][str(ctx.channel.id)] = city
            self.saveConfigs()
            await ctx.send("Pokestop research channel updated")

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


async def setup(bot):
    await bot.add_cog(ConfigsCog(bot))
