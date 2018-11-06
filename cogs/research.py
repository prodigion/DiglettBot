import discord
from discord.ext import commands

class ResearchCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dig')
    @commands.guild_only()
    async def get_quests(self, ctx, mon):
        """List all encounters for a specific Pokemon. Can either be searched by Pokemon name or number."""

        try:
            monName = mon
            mon = next(key for key, value in self.bot.pokedex.items() if value.lower() == mon.lower())
        except StopIteration:
            pass

        try:
            monName = self.bot.pokedex[mon]
        except KeyError:
            mon = 0

        if ctx.channel.name == "pokestop-reports":
            async with self.bot.pool.acquire() as conn:
                try:
                    async with conn.cursor() as cur:
                        await cur.execute(f"select * from pokestop where quest_pokemon_id={mon};")
                        numResults = cur.rowcount
                        if numResults == 0:
                            await ctx.send(f"No results found for {monName}")
                        ctr = 0
                        questList = f"Today's Research - {monName}\n\n"
                        async for r in cur:
                            ctr += 1
                            questList += f'({ctr}/{numResults}) Poketop: [{r[3]}](http://www.google.com/maps/place/{r[1]},{r[2]})\n'
                            if len(questList) > 1500 or ctr == numResults:
                                await ctx.send(embed=discord.Embed(description=questList))
                                questList = f"Today's Research - {monName}\n\n"
                except pymysql.err.OperationalError:
                    await ctx.send('Server is not currently available. Please try again later.')

def setup(bot):
    bot.add_cog(ResearchCog(bot))
