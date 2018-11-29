import discord
from discord.ext import commands
import aiomysql
from pymysql.err import OperationalError
import datetime

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

    async def get_quests(self, ctx, cur, mon: int, type = "encounter"):
        """List all quests for a specific reward."""

        if type == "encounter":
            reward = self.bot.pokedex[f'{mon:03}']
        elif type == "item":
            reward = self.bot.items[f'{mon}']

        header = f"Research for {datetime.date.today():%B %d} - {reward}\n" \
                 f"{self.numScannedStops} of {self.numStops} ({int(100 * self.numScannedStops/self.numStops)}%) PokeStops scanned.\n\n"

        if type == "encounter":
            await cur.execute(f"select * from pokestop where quest_pokemon_id={mon};")
        elif type == "item":
            await cur.execute(f"select * from pokestop where quest_item_id={mon};")

        numResults = cur.rowcount
        if numResults == 0:
            if type == "encounter":
                await ctx.send(embed=discord.Embed(description=f"No results found for {self.bot.pokedex[f'{mon:03}']}."))
            elif type == "item":
                await ctx.send(embed=discord.Embed(description=f"No results found for {self.bot.items[f'{mon}']}."))
        ctr = 0
        questList = header
        async for r in cur:
            ctr += 1
            questList += f'({ctr}/{numResults}) PokeStop: [{r[3]}](http://www.google.com/maps/place/{r[1]},{r[2]})\n'
            if len(questList) > 1850 or ctr == numResults:
                await ctx.send(embed=discord.Embed(description=questList))
                await ctx.author.send(embed=discord.Embed(description=questList))
                questList = header

    async def get_encounters(self, ctx, cur, mon: int):
        """List all encounters for a specific Pokemon."""

        header = f"Research for {datetime.date.today():%B %d} - {self.bot.pokedex[f'{mon:03}']}\n" \
                 f"{self.numScannedStops} of {self.numStops} ({int(100 * self.numScannedStops/self.numStops)}%) PokeStops scanned.\n\n"

        await cur.execute(f"select * from pokestop where quest_pokemon_id={mon};")
        numResults = cur.rowcount
        if numResults == 0:
            await ctx.send(embed=discord.Embed(description=f"No results found for {self.bot.pokedex[f'{mon:03}']}."))
        ctr = 0
        questList = header
        async for r in cur:
            ctr += 1
            questList += f'({ctr}/{numResults}) PokeStop: [{r[3]}](http://www.google.com/maps/place/{r[1]},{r[2]})\n'
            if len(questList) > 1850 or ctr == numResults:
                await ctx.send(embed=discord.Embed(description=questList))
                await ctx.author.send(embed=discord.Embed(description=questList))
                questList = header

    @commands.command(name='dig')
    @commands.guild_only()
    async def get_research(self, ctx, monName = ""):
        """List all encounters for a specific Pokemon."""

        type = "mon"
        if ctx.channel.name == "pokestop-reports":
            if monName == "":
                await ctx.send("Please select a mon or item to search for. For example, `!dig Chansey`")
                return
            try:
                try:
                    mon = next(key for key, value in self.bot.pokedex.items() if value.lower() == monName.lower())
                    monName = self.bot.pokedex[mon]
                except StopIteration:
                    mon = next(key for key, value in self.bot.items.items() if value.lower() == monName.lower())
                    monName = self.bot.items[mon]
                    type = "item"
            except StopIteration:
                mon = 0

            try:
                await self.get_stats(ctx)
                async with self.bot.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        if type == "mon":
                            await self.get_encounters(ctx, cur, int(mon))
                        elif type == "item":
                            await self.get_quests(ctx, cur, int(mon), "items")
            except (OperationalError, RuntimeError):
                await ctx.send('Server is not currently available. Please try again later or use Meowth reporting.')

    @commands.command(name='dugtrio')
    @commands.guild_only()
    @commands.has_role('Admins')
    async def get_all_research(self, ctx, type=""):
        """List all encounters, sorted by Pokemon number"""

        if ctx.channel.name == "pokestop-reports" or ctx.channel.name == "mod-spam":
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if type == "items":
                        await cur.execute(f"select distinct quest_item_id from pokestop;")
                    else:
                        await cur.execute(f"select distinct quest_pokemon_id from pokestop;")
                    numResults = cur.rowcount
                    if numResults <= 1:
                        await ctx.send(f"No research found")
                    async with self.bot.pool.acquire() as conn2:
                        async with conn.cursor() as cur2:
                            async for r in cur:
                                print(r)
                                if r[0]:
                                    if type == "items":
                                        await self.get_quests(ctx, cur2, r[0], "items")
                                    else:
                                        await self.get_encounters(ctx, cur2, r[0])

    @commands.command(name='reconnect')
    @commands.guild_only()
    @commands.has_role('Admins')
    async def reconnect(self, ctx):
        """List all encounters, sorted by Pokemon number"""

        try:
            if self.bot.pool:
                self.bot.pool.close()
                await self.bot.pool.wait_closed()
            self.bot.pool = await aiomysql.create_pool(host=self.bot.configs['host'], port=self.bot.configs['port'],
                                                       user=self.bot.configs['user'], password=self.bot.configs['pass'],
                                                       db=self.bot.configs['db'], autocommit=True)
            await ctx.send("Success")
        except:
            await ctx.send("Failure")

def setup(bot):
    bot.add_cog(ResearchCog(bot))
