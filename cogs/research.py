import discord
from discord.ext import commands
import aiomysql
from pymysql.err import OperationalError
import datetime
import json

class ResearchCog:
    def __init__(self, bot):
        self.bot = bot

    async def get_stats(self, ctx):
        """How many pokestops have been scanned."""

        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"select count(*) from pokestop;")
                (self.numStops,) = await cur.fetchone()
                await cur.execute(f"select count(*) from pokestop where quest_type is not null;")
                (self.numScannedStops,) = await cur.fetchone()

    def parse_quest_type(self, type, target):
        return f"{self.bot.data['quests']['types'][type]} ({target})"

    def parse_quest_conditions(self, conditions):
        data = self.bot.data['quests']['conditions']
        if not conditions: return ""
        out = ""
        for condition in conditions:
            print(condition)
            out += f"{data[condition['type']]} "
            if condition.get('info'):
                if condition['info'].get('throw_type_id'): out += f"{self.bot.data['activities'][condition['info']['throw_type_id']]} "
                if condition['info'].get('pokemon_type_ids'):
                    for type in condition['info']['pokemon_type_ids']:
                        out += f"{self.bot.data['pokemon_types'][type]} "
                if condition['info'].get('pokemon_ids'):
                    for pokemon in condition['info']['pokemon_ids']:
                        out += f"{self.bot.data['pokemon'][pokemon]} "
                if condition['info'].get('raid_levels'): out += str(condition['info']['raid_levels']) + " "
        return out + "\n"

    async def get_quests(self, ctx, cur, mon: int, type):
        """List all quests for a specific reward."""

        if type == "encounters":
            reward = self.bot.data['pokedex'][mon]
        elif type == "items":
            reward = self.bot.data['items'][mon]
        elif type == "stardust":
            reward = f'Stardust ({mon})' if mon else 'Stardust'

        header = f"Research for {datetime.date.today():%B %d} - {reward}\n" \
                 f"{self.numScannedStops} of {self.numStops} ({int(100 * self.numScannedStops/self.numStops)}%) PokeStops scanned.\n"

        if type == "encounters":
            await cur.execute(f"select quest_type, quest_target, quest_conditions from pokestop where quest_reward_type = 7 and quest_pokemon_id={mon} limit 1;")
            async for r in cur:
                header += self.parse_quest_type(r[0], r[1]) + "\n"
                header += self.parse_quest_conditions(json.loads(r[2]))
            await cur.execute(f"select name, lat, lon from pokestop where quest_reward_type = 7 and quest_pokemon_id={mon};")
        elif type == "items":
#            await cur.execute(f"select quest_type, quest_target, quest_conditions from pokestop where quest_reward_type = 2 and quest_item_id={mon} limit 1;")
#            async for r in cur:
#                header += self.bot.data['quests']['types'][str(r[0])] + f" ({r[1]})" + str(r[2]) + "\n"
            await cur.execute(f"select name, lat, lon, json_extract(json_extract(quest_rewards,_utf8mb4'$[*].info'),_utf8mb4'$[0].amount') from pokestop where quest_reward_type = 2 and quest_item_id={mon};")
        elif type == "stardust":
            await cur.execute(f"select name, lat, lon from pokestop where quest_reward_type = 3 and json_extract(json_extract(quest_rewards,_utf8mb4'$[*].info'),_utf8mb4'$[0].amount') = {mon};")

        numResults = cur.rowcount
        if numResults == 0:
            if type == "encounters":
                await ctx.send(embed=discord.Embed(description=f"No results found for {self.bot.data['pokedex'][mon]}."))
            elif type == "items":
                await ctx.send(embed=discord.Embed(description=f"No results found for {self.bot.data['items'][mon]}."))
            elif type == "stardust":
                await ctx.send(embed=discord.Embed(description=f"No results found for Stardust ({mon})."))
        ctr = 0
        questList = header + "\n"
        async for r in cur:
            ctr += 1
            questList += f'({ctr}/{numResults}) PokeStop: [{r[0]}](http://www.google.com/maps/place/{r[1]},{r[2]})\n'
            if len(questList) > 1850 or ctr == numResults:
                await ctx.send(embed=discord.Embed(description=questList))
                await ctx.author.send(embed=discord.Embed(description=questList))
                questList = header + "\n"

    @commands.command(name='dig')
    @commands.guild_only()
    async def get_research(self, ctx, monName = "", amount = 0):
        """List all encounters for a specific Pokemon."""

        if ctx.channel.name == "pokestop-reports" or ctx.channel.name == "mod-spam":
            if monName == "":
                await ctx.send("Please select a valid mon or item to search for. For example, `!dig Chansey`")
                return
            elif monName.lower() == "stardust":
                type = "stardust"
                mon = amount # use mon to store stardust reward amount
            else:
                try:
                    try:
                        mon = next(key for key, value in self.bot.data['pokedex'].items() if value.lower() == monName.lower())
                        monName = self.bot.data['pokedex'][mon]
                        type = "encounters"
                    except StopIteration:
                        mon = next(key for key, value in self.bot.data['items'].items() if value.lower() == monName.lower())
                        monName = self.bot.data['items'][mon]
                        type = "items"
                except StopIteration:
                    mon = 0

            if mon == 0:
                await ctx.send("Please select a valid mon or item to search for. For example, `!dig Chansey`")
                return

            try:
                await self.get_stats(ctx)
                async with self.bot.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await self.get_quests(ctx, cur, int(mon), type)
            except (OperationalError, RuntimeError, AttributeError):
                await ctx.send('Server is not currently available. Please try again later or use Meowth reporting.')

    @commands.command(name='dugtrio')
    @commands.guild_only()
    @commands.has_role('Admins')
    async def get_all_research(self, ctx, type="encounters"):
        """List all encounters, sorted by Pokemon number"""

        if ctx.channel.name == "pokestop-reports" or ctx.channel.name == "mod-spam":
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if type == "encounters":
                        await cur.execute(f"select quest_pokemon_id, quest_template, count(*) from pokestop where quest_reward_type = 7 group by quest_pokemon_id, quest_template order by quest_pokemon_id;")
                    elif type == "items":
                        await cur.execute(f"select quest_item_id, quest_template, count(*) from pokestop where quest_reward_type = 2 group by quest_item_id, quest_template order by quest_item_id;")
                    elif type == "stardust":
                        await cur.execute(f"select json_extract(json_extract(quest_rewards,_utf8mb4'$[*].info'),_utf8mb4'$[0].amount') as amount, quest_template, count(*) from pokestop where quest_reward_type = 3 group by amount, quest_template order by amount;")

                    numResults = cur.rowcount
                    if numResults <= 1:
                        await ctx.send(f"No research found")
                    await self.get_stats(ctx)

                    ctr = 0
                    header = f"Available research for {datetime.date.today():%B %d}\n" \
                             f"{self.numScannedStops} of {self.numStops} ({int(100 * self.numScannedStops/self.numStops)}%) PokeStops scanned.\n"

                    questList = header + "\n"
                    async for r in cur:
                        ctr += 1
                        if type == "encounters":
                            reward = self.bot.data['pokedex'][r[0]]
                        elif type == "items":
                            reward = self.bot.data['items'][r[0]]
                        elif type == "stardust":
                            reward = f'Stardust ({r[0]})'

                        questList += f'{r[2]} quests for {reward} <{r[1]}>\n'
                        if len(questList) > 1850 or ctr == numResults:
                            await ctx.send(embed=discord.Embed(description=questList))
                            questList = header + "\n"

    @commands.command(name='map')
    @commands.guild_only()
    async def set_map(self, ctx):
        """Set map-notifications role"""
        if ctx.channel.name == "role-select":
            role = discord.utils.get(ctx.guild.roles, name=ctx.invoked_with)
            if role in ctx.author.roles:
                await ctx.author.remove_roles(role)
                await ctx.send(f'Role removed: ' + role.name)
            else:
                await ctx.author.add_roles(role)
                await ctx.send(f'Role added: ' + role.name)

    @commands.command(name='reconnect')
    @commands.guild_only()
    @commands.has_role('Admins')
    async def reconnect(self, ctx):
        """Reconnect to map DB"""
        try:
            await self.connectDB(ctx.guild.id)
            await ctx.send("Success")
        except:
            await ctx.send("Failure")

    async def connectDB(self, guild):
        try:
            self.bot.pool.close()
            await self.bot.pool.wait_closed()
        except:
            pass
        guild = str(guild)
        self.bot.pool = await aiomysql.create_pool(host=self.bot.configs[guild]['host'], port=self.bot.configs[guild]['port'],
                                                   user=self.bot.configs[guild]['user'], password=self.bot.configs[guild]['pass'],
                                                   db=self.bot.configs[guild]['db'], autocommit=True)

def setup(bot):
    bot.add_cog(ResearchCog(bot))
