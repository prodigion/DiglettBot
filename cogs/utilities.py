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

    @commands.command(name='say', aliases=['copy', 'mimic'])
    @commands.is_owner()
    async def do_say(self, ctx, *, comment: str):
        """A simple command which repeats our input."""

        await ctx.message.delete()
        await ctx.send(comment)

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

        # Forbid Babies, Regionals, Special Research, item evolves, Gen2/3 unreleased, Gen4 unreleased
        forbiddenRoles = ['pichu', 'cleffa', 'igglybuff', 'togepi', 'tyrogue', 'smoochum', 'elekid', 'magby', 'azurill', 'wynaut', 'budew', 'chingling', 'bonsly', 'mime jr', 'happiny', 'munchlax', 'riolu', 'mantyke',
                          'corsola', "farfetch'd", 'heracross', 'kangaskhan', 'mr mime', 'relicanth', 'solrock', 'torkoal', 'tropius', 'volbeat', 'zangoose', 'pachirisu', 'chatot', 'carnivine',
                          'celebi', 'jirachi', 'mew', 'phione', 'manaphy', 'darkrai', 'shaymin', 'arceus', 'spiritomb',
                          'espeon', 'flygon', 'gardevoir', 'kingdra', 'ludicolo', 'metagross', 'milotic', 'porygon2', 'salamence', 'scizor', 'slaking', 'steelix', 'sunflora', 'umbreon', 'wailord', 'floatzel',
                          'smeargle', 'kecleon', 'clamperl', 'huntail', 'gorebyss',
                          'roserade', 'cranidos', 'rampardos', 'shieldon', 'bastiodon', 'burmy', 'wormadam', 'mothim', 'combee', 'vespiquen', 'cherubi', 'cherrim', 'shellos', 'gastrodon', 'ambipom', 'mismagius', 'honchkrow', 'glameow', 'purugly', 'bronzor', 'bronzong', 'gible', 'gabite', 'garchomp', 'hippopotas', 'hippowdon', 'skorupi', 'drapion', 'croagunk', 'toxicroak', 'finneon', 'lumineon', 'snover', 'abomasnow', 'weavile', 'magnezone', 'lickilicky', 'rhyperior', 'tangrowth', 'electivire', 'magmortar', 'togekiss', 'yanmega', 'leafeon', 'glaceon', 'gliscor', 'mamoswine', 'porygon z', 'gallade', 'probopass', 'dusknoir', 'froslass', 'rotom'
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

def setup(bot):
    bot.add_cog(UtilityCog(bot))
