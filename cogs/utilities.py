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
          await ctx.send(self.bot.configs[str(ctx.guild.id)]['nests'])

        await ctx.message.delete()

    @commands.command(name='cleanroles')
    @commands.has_role('Mods')
    @commands.guild_only()
    async def clean_roles(self, ctx):
        """Clean Roles"""

        # Forbid Babies, Regionals, Special Research, Legendary (1, 2, 3, 4), Uncatchable (2, 3, 4), Unreleased (1, 2, 3, 4)
        forbiddenRoles = ['pichu', 'cleffa', 'igglybuff', 'togepi', 'tyrogue', 'smoochum', 'elekid', 'magby', 'azurill', 'wynaut', 'budew', 'chingling', 'bonsly', 'mime jr', 'happiny', 'munchlax', 'riolu', 'mantyke',
                          'corsola', "farfetch'd", 'heracross', 'kangaskhan', 'mr mime', 'relicanth', 'lunatone', 'torkoal', 'tropius', 'volbeat', 'zangoose', 'pachirisu', 'chatot', 'carnivine',
                          'celebi', 'jirachi', 'mew', 'phione', 'manaphy', 'darkrai', 'shaymin', 'arceus', 'spiritomb', 'meltan', 'melmetal',
                          'articuno', 'moltres', 'zapdos', 'mewtwo',
                          'raikou', 'entei', 'suicune', 'lugia', 'ho-oh',
                          'regirock', 'regice', 'registeel', 'latias', 'latios', 'kyogre', 'groudon', 'rayquaza', 'deoxys',
                          'dialga', 'palkia', 'heatran', 'regigigas', 'giratina', 'cresselia',
                          'bellossom', 'politoed', 'sunflora', 'espeon', 'umbreon', 'slowking', 'steelix', 'scizor', 'kingdra', 'porygon2',
                          'nincada', 'ninjask', 'mawile', 'spinda', 'altaria', 'milotic', 'absol',
                          'roserade', 'mismagius', 'honchkrow', 'weavile', 'magnezone', 'lickilicky', 'rhyperior', 'tangrowth', 'electivire', 'magmortar', 'togekiss', 'yanmega', 'leafeon', 'glaceon', 'gliscor', 'mamoswine', 'porygon z', 'gallade', 'probopass', 'dusknoir', 'froslass',
                          'smeargle', 'kecleon',
                          'rampardos', 'bastiodon', 'wormadam', 'mothim', 'vespiquen', 'gastrodon', 'ambipom', 'garchomp', 'rotom'
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
