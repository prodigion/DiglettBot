import discord
from discord.ext import commands

class ResearchCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dig')
    @commands.guild_only()
    async def get_quests(self, ctx, mon: int):
        """Query quests"""

        if ctx.channel.name == "pokestop-reports":
            async with self.bot.pool.acquire() as conn:
                try:
                    async with conn.cursor() as cur:
                        await cur.execute(f"select * from pokestop where quest_pokemon_id={mon};")
                        numResults = cur.rowcount
                        ctr = 0
                        async for r in cur:
                            ctr += 1
                            await ctx.send(f'({ctr}/{numResults}) - Stop: {r[3]} - <http://www.google.com/maps/place/{r[1]},{r[2]}>')
                except pymysql.err.OperationalError:
                    await ctx.send('Server is not currently available. Please try again later.')

def setup(bot):
    bot.add_cog(ResearchCog(bot))
