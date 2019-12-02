import discord
from discord.ext import commands
import aiomysql
from pymysql.err import OperationalError
import datetime
import json

class ResearchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_check(ctx):
        role = discord.utils.get(ctx.guild.roles, id=ctx.bot.configs[str(ctx.guild.id)]['admin-role'])
        return role in ctx.author.roles

    async def get_stats(self, ctx):
        """How many pokestops have been scanned."""

        async with self.bot.pool[str(ctx.guild.id)].acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"select count(*) from pokestop where url is not null;")
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
#            print(condition)
            out += f"{data[condition['type']]} "
            if condition.get('info'):
                if condition['info'].get('throw_type_id'): out += f"{self.bot.data['activities'][condition['info']['throw_type_id']]} "
                if condition['info'].get('pokemon_type_ids'):
                    for type in condition['info']['pokemon_type_ids']:
                        out += f"{self.bot.data['pokemon_types'][type]} "
                if condition['info'].get('pokemon_ids'):
                    for pokemon in condition['info']['pokemon_ids']:
                        out += f"{self.bot.data['pokedex'][pokemon]} "
#                if condition['info'].get('hit'): out += "in a row "
                if condition['info'].get('raid_levels'): out += str(condition['info']['raid_levels']) + " "
        return out

    def parse_quest_template(self, template):
        try:
            return self.bot.data['quests']['templates'][template]
        except:
            return ""

    async def get_quests(self, ctx, cur, mon: int, type):
        """List all quests for a specific reward."""

        if type == "encounters":
            reward = self.bot.data['pokedex'][mon]
            await cur.execute(f"select quest_template, quest_type, quest_target, quest_conditions from pokestop where quest_reward_type = 7 and quest_pokemon_id = {mon} group by quest_template;")
        elif type == "items":
            await cur.execute(f"select quest_template, quest_type, quest_target, quest_conditions, json_extract(json_extract(quest_rewards,_utf8mb4'$[*].info'),_utf8mb4'$[0].amount') from pokestop where quest_reward_type = 2 and quest_item_id = {mon} group by quest_template;")
        elif type == "stardust":
            reward = f'<:stardust:543911550734434319>{mon}'
            await cur.execute(f"select quest_template, quest_type, quest_target, quest_conditions from pokestop where quest_reward_type = 3 and json_extract(json_extract(quest_rewards,_utf8mb4'$[*].info'),_utf8mb4'$[0].amount') = {mon} group by quest_template;")

        numTemplates = cur.rowcount
        if numTemplates == 0:
            if type == "encounters":
                await ctx.send(embed=discord.Embed(description=f"No results found for {self.bot.data['pokedex'][mon]}."))
            elif type == "items":
                await ctx.send(embed=discord.Embed(description=f"No results found for {self.bot.data['items'][mon]}."))
            elif type == "stardust":
                await ctx.send(embed=discord.Embed(description=f"No results found for <:stardust:543911550734434319>{mon}."))
        ctr = 0
        questList = ""
        results = await cur.fetchall()
        for r in results:
            ctr += 1
            if type == "items": reward = f"{self.bot.data['items'][mon]} ({r[4]})"
            header = f"Research for {datetime.date.today():%B %d} - {reward}\n" \
                     f"{self.numScannedStops} of {self.numStops} ({int(100 * self.numScannedStops/self.numStops)}%) PokeStops scanned.\n"
            footer = ""
            if self.bot.configs[str(ctx.guild.id)]['map-info']: footer = "\n" + self.bot.configs[str(ctx.guild.id)]['map-info']

            template = r[0]
            questRequirement = self.parse_quest_template(r[0])
            if questRequirement == "":
                    questRequirement = self.parse_quest_type(r[1], r[2]) + "\n" + self.parse_quest_conditions(json.loads(r[3]))
            questList += header + questRequirement + "\n\n"

            async with self.bot.pool[str(ctx.guild.id)].acquire() as conn:
                async with conn.cursor() as cur2:
                    if type == "encounters":
                        await cur2.execute(f"select name, lat, lon from pokestop where quest_reward_type = 7 and quest_pokemon_id={mon} and quest_template = '{r[0]}';")
                    elif type == "items":
                        await cur2.execute(f"select name, lat, lon from pokestop where quest_reward_type = 2 and quest_item_id={mon} and quest_template = '{r[0]}';")
                    elif type == "stardust":
                        await cur2.execute(f"select name, lat, lon from pokestop where quest_reward_type = 3 and json_extract(json_extract(quest_rewards,_utf8mb4'$[*].info'),_utf8mb4'$[0].amount') = {mon} and quest_template = '{r[0]}';")

                    numResults = cur2.rowcount
                    ctr2 = 0
                    results2 = await cur2.fetchall()
                    for r2 in results2:
                        ctr2 += 1
                        questList += f'({ctr2}/{numResults}) PokeStop: [{r2[0]}](http://www.google.com/maps/place/{r2[1]},{r2[2]})\n'
                        if len(questList + footer) > 1850 or ctr2 == numResults and ctr == numTemplates:
                            await ctx.send(embed=discord.Embed(description=questList + footer))
                            await ctx.author.send(embed=discord.Embed(description=questList + footer))
                            if ctr2 == numResults:
                                questList = ""
                            else:
                                questList = header + questRequirement + "\n\n"
                        elif ctr2 == numResults: questList += "\n"

    async def get_rocket(self, ctx, cur, type):
        """List all currently know rocket locations."""

        if type == "executive":
            grunt_query = "(41,42,43)"
            header = f"On {datetime.date.today():%B %d} Team Rocket Executive can be found until 10:00PM...\n\n"
        elif type == "giovanni":
            grunt_query = "(44,45,46)"
            header = f"On {datetime.date.today():%B %d} Team Rocket Giovanni or Decoy can be found until 10:00PM...\n\n"
        else:
            grunt_query = "(4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,47,48,49,50)"
            header = f"On {datetime.datetime.now():%B %d @ %I:%M %p} Team Rocket can be found until...\n\n"

        await cur.execute(f"select name, lat, lon, incident_expire_timestamp from pokestop where incident_expire_timestamp is not null and grunt_type in {grunt_query} order by incident_expire_timestamp desc;")

        numResults = cur.rowcount
        if numResults == 0:
            await ctx.send(embed=discord.Embed(description=f"Team Rocket is in hiding! No results found"))

        footer = ""
        if self.bot.configs[str(ctx.guild.id)]['map-info']: footer = "\n" + self.bot.configs[str(ctx.guild.id)]['map-info']

        ctr = 0
        rocketList = header
        results = await cur.fetchall()
        for r in results:
            ctr += 1
            if type == "grunt":
                rocketList += f'{datetime.datetime.fromtimestamp(int(r[3])):%I:%M %p} at [{r[0]}](http://www.google.com/maps/place/{r[1]},{r[2]})\n'
            else:
                rocketList += f'at [{r[0]}](http://www.google.com/maps/place/{r[1]},{r[2]})\n'
            if len(rocketList + footer) > 1850 or ctr == numResults:
                await ctx.send(embed=discord.Embed(description=rocketList + footer))
                rTime = datetime.datetime.fromtimestamp(int(r[3])) - datetime.datetime.now()
                if rTime.seconds < 900: return
                if ctr != numResults:
                    rocketList = header

    @commands.command(name='dig')
    @commands.guild_only()
    async def get_research(self, ctx, *, researchString):
        """Scan database for pokestop research and rocket encounters."""

        if ctx.channel.id == self.bot.configs[str(ctx.guild.id)]['research-channel'] or ctx.channel.name == "pokestop-reports" or ctx.channel.name == "mod-spam":
            if researchString == "":
                await ctx.send("Please select a valid mon or item to search for. For example, `!dig Chansey`")
                return
            elif researchString[:8].lower() == "stardust":
                type = "stardust"
                try:
                    amount = int(researchString[8:])
                except ValueError:
                    amount = 0
                if amount == 0:
                    await ctx.send("Please select a stardust value to search for. For example, `!dig stardust 1000`")
                else:
                    mon = amount # use mon to store stardust reward amount
            elif researchString.lower() in ["grunt", "executive", "giovanni"]:
                type = "rocket"
                mon = researchString.lower()

            else:
                try:
                    try:
                        mon = next(key for key, value in self.bot.data['pokedex'].items() if value.lower() == researchString.lower())
                        researchString = self.bot.data['pokedex'][mon]
                        type = "encounters"
                    except StopIteration:
                        mon = next(key for key, value in self.bot.data['items'].items() if value.lower() == researchString.lower())
                        researchString = self.bot.data['items'][mon]
                        type = "items"
                except StopIteration:
                    mon = 0

            if mon == 0:
                await ctx.send("Please select a valid mon or item to search for. For example, `!dig Chansey`")
                return

            try:
                if type == "rocket":
                    async with self.bot.pool[str(ctx.guild.id)].acquire() as conn:
                        async with conn.cursor() as cur:
                            await self.get_rocket(ctx, cur, mon)
                else:
                    await self.get_stats(ctx)
                    async with self.bot.pool[str(ctx.guild.id)].acquire() as conn:
                        async with conn.cursor() as cur:
                            await self.get_quests(ctx, cur, int(mon), type)
            except (OperationalError, RuntimeError, AttributeError):
                await self.connectDBFail(ctx)

    @commands.command(name='trio')
    @commands.guild_only()
    @commands.check(is_admin_check)
    async def get_all_research(self, ctx, type="encounters"):
        """List all encounters, sorted by Pokemon number"""

        missingQuestTemplates = []
        if ctx.channel.id == self.bot.configs[str(ctx.guild.id)]['research-channel'] or ctx.channel.name == "pokestop-reports" or ctx.channel.name == "mod-spam":
            try:
                async with self.bot.pool[str(ctx.guild.id)].acquire() as conn:
                    async with conn.cursor() as cur:
                        if type == "encounters":
                            await cur.execute(f"select quest_pokemon_id, quest_template, quest_conditions, count(*) from pokestop where quest_reward_type = 7 group by quest_pokemon_id, quest_template order by quest_pokemon_id;")
                        elif type == "items":
                            await cur.execute(f"select quest_item_id, quest_template, quest_conditions, count(*) from pokestop where quest_reward_type = 2 group by quest_item_id, quest_template order by quest_item_id;")
                        elif type == "stardust":
                            await cur.execute(f"select json_extract(json_extract(quest_rewards,_utf8mb4'$[*].info'),_utf8mb4'$[0].amount') as amount, quest_template, quest_conditions, count(*) from pokestop where quest_reward_type = 3 group by amount, quest_template order by amount;")

                        numResults = cur.rowcount
                        if numResults <= 1:
                            await ctx.send(f"No research found")
                        await self.get_stats(ctx)

                        ctr = 0
                        header = f"Available research for {datetime.date.today():%B %d}\n" \
                                 f"{self.numScannedStops} of {self.numStops} ({int(100 * self.numScannedStops/self.numStops)}%) PokeStops scanned.\n"
                        footer = ""
                        if self.bot.configs[str(ctx.guild.id)]['map-info']: footer = "\n" + self.bot.configs[str(ctx.guild.id)]['map-info']

                        questList = header + "\n"
                        results = await cur.fetchall()
                        for r in results:
                            ctr += 1
                            if type == "encounters":
                                reward = self.bot.data['pokedex'][r[0]]
                            elif type == "items":
                                reward = self.bot.data['items'][r[0]]
                            elif type == "stardust":
                                reward = f'<:stardust:543911550734434319>{r[0]}'

                            questRequirement = self.parse_quest_template(r[1])
                            if questRequirement == "":
    #                            print(r)
                                questRequirement = f"<{r[1]}> " + self.parse_quest_conditions(json.loads(r[2]))
                                missingQuestTemplates.append(r[1])
                            questList += f'{r[3]} quests for {reward} ({questRequirement})\n'
                            if len(questList + footer) > 1850 or ctr == numResults:
                                await ctx.send(embed=discord.Embed(description=questList + footer))
                                questList = header + "\n"
            except (OperationalError, RuntimeError, AttributeError):
                await self.connectDBFail(ctx)

            if missingQuestTemplates: await ctx.send(embed=discord.Embed(description="Undefined quests\n\n" + "\n".join(set(missingQuestTemplates))))

    @commands.command(name='map')
    @commands.guild_only()
    async def set_map(self, ctx):
        """Set map-notifications role"""
        if ctx.channel.id == self.bot.configs[str(ctx.guild.id)]['role-channel']:
            role = discord.utils.get(ctx.guild.roles, name=ctx.invoked_with)
            if role in ctx.author.roles:
                await ctx.author.remove_roles(role)
                await ctx.send(f'Role removed: ' + role.name)
            else:
                await ctx.author.add_roles(role)
                await ctx.send(f'Role added: ' + role.name)

    @commands.command(name='reconnect')
    @commands.guild_only()
    @commands.check(is_admin_check)
    async def reconnect(self, ctx):
        """Reconnect to map DB"""
        try:
            await self.connectDB(ctx.guild)
            await ctx.send("Success")
        except:
            await ctx.send("Failure")

    async def connectDB(self, guild):
        guild = str(guild.id)

        try:
            self.bot.pool[guild].close()
            await self.bot.pool[guild].wait_closed()
        except:
            pass

        self.bot.pool[guild] = await aiomysql.create_pool(host=self.bot.configs[guild]['host'], port=self.bot.configs[guild]['port'],
                                                          user=self.bot.configs[guild]['user'], password=self.bot.configs[guild]['pass'],
                                                          db=self.bot.configs[guild]['db'], autocommit=True)

    async def connectDBFail(self, ctx):
        await ctx.send('Server is not currently available. Please try again later or use Meowth reporting.')

def setup(bot):
    bot.add_cog(ResearchCog(bot))
