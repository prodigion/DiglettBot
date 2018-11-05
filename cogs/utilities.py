import discord
from discord.ext import commands

"""Utility functions"""

class UtilityCog:
    """UtilityCog"""

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

    @commands.command(name='nests')
    @commands.guild_only()
    async def print_nests(self, ctx):
        """Print nests"""

        if ctx.channel.name == "migration-chat":
          await ctx.send(f'Reposting NestDoc links; see below...\n\nhttps://goo.gl/jRvJWH (Active nests)\nhttps://goo.gl/hQ5B7B (Submit nesting Pokemon)')

        await ctx.message.delete()

    @commands.command(name='cleanroles')
    @commands.has_role('Mods')
    @commands.guild_only()
    async def clean_roles(self, ctx):
        """Clean Roles"""

        forbiddenRoles = ['pichu', 'togepi', 'elekid', 'magby', 'smoochum', 'tyrogue', 'azurill', 'wynaut', 'riolu', 'mime jr', 'munchlax',
                          'corsola', "farfetch'd", 'heracross', 'kangaskhan', 'mr mime', 'relicanth', 'solrock', 'torkoal', 'tropius', 'volbeat', 'zangoose', 'pachirisu', 'chatot', 'carnivine',
                          'celebi', 'jirachi', 'mew',
                          'delibird', 'espeon', 'flygon', 'gardevoir', 'kingdra', 'ludicolo', 'metagross', 'milotic', 'porygon2', 'salamence', 'scizor', 'slaking', 'steelix', 'sunflora', 'umbreon', 'wailord',
                          'gorebyss', 'huntail', 'kecleon', 'smeargle',
                          'budew', 'roserade', 'cranidos', 'rampardos', 'shieldon', 'bastiodon', 'burmy', 'wormadam', 'mothim', 'combee', 'vespiquen', 'buizel', 'floatzel', 'cherubi', 'cherrim', 'shellos', 'gastrodon', 'ambipom', 'mismagius', 'honchkrow', 'glameow', 'purugly', 'chingling', 'bronzor', 'bronzong', 'bonsly', 'happiny', 'spiritomb', 'gible', 'gabite', 'garchomp', 'hippopotas', 'hippowdon', 'skorupi', 'drapion', 'croagunk', 'toxicroak', 'finneon', 'lumineon', 'mantyke', 'snover', 'abomasnow', 'weavile', 'magnezone', 'lickilicky', 'rhyperior', 'tangrowth', 'electivire', 'magmortar', 'togekiss', 'yanmega', 'leafeon', 'glaceon', 'gliscor', 'mamoswine', 'porygon z', 'gallade', 'probopass', 'dusknoir', 'froslass', 'rotom', 'uxie', 'mesprit', 'azelf', 'dialga', 'palkia', 'heatran', 'regigigas', 'cresselia', 'phione', 'manaphy', 'darkrai', 'shaymin', 'arceus'
                         ]
        clearedRoles = 0
        for delRole in forbiddenRoles:
          role = discord.utils.get(ctx.guild.roles, name=delRole)
          if role:
            try:
              await role.delete()
              await ctx.send(f"The role {role.name} has been deleted!")
              clearedRoles += 1
            except discord.Forbidden:
              await ctx.send("Missing Permissions to delete this role!")

        await ctx.send(f"{clearedRoles} Roles cleared.")

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(UtilityCog(bot))
