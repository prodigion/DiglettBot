import discord
from discord.ext import commands


class WelcomeView(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot

        super().__init__(timeout=None)

    @discord.ui.button(label="Valor", emoji="<:valor:408859732280082444>", custom_id="welcomeview:valor")
    async def callback_valor(self, interaction, button):
        await self.processTeamSelect(interaction, "valor")

    @discord.ui.button(label="Mystic", emoji="<:mystic:408859736134516759>", custom_id="welcomeview:mystic")
    async def callback_mystic(self, interaction, button):
        await self.processTeamSelect(interaction, "mystic")

    @discord.ui.button(label="Instinct", emoji="<:instinct:408859733831843867>", custom_id="welcomeview:instinct")
    async def callback_instinct(self, interaction, button):
        await self.processTeamSelect(interaction, "instinct")

    @discord.ui.button(label="Harmony", emoji="<:harmony:509206588553297930>", custom_id="welcomeview:harmony")
    async def callback_harmony(self, interaction, button):
        await self.processTeamSelect(interaction, "harmony")

    async def processTeamSelect(self, interaction, team_choice):
        harmony_role = discord.utils.get(interaction.guild.roles, name="harmony")
        if harmony_role in interaction.user.roles:
            if team_choice == "harmony":
                await interaction.response.send_message(f"You're already on team Harmony!", ephemeral=True)
                return
            else:
                await interaction.user.remove_roles(harmony_role)
        await interaction.response.send_message(f'Welcome to team {team_choice.capitalize()}!', ephemeral=True)
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name=team_choice),
                                         discord.utils.get(interaction.guild.roles, name="chat"),
                                         atomic=True)

        welcomeMsg = f"Now that you've selected a team, {interaction.user.mention}, the below commands are available.\n" \
                     f"They work as toggles so you can join/leave them as you require. Join as many as you'd like!\n" \
                     f"Tag `@Mods` or `@Coordinators` if you have any questions."

        teamSelectMessage = (
          f"\n"
          f"Regions of Ontario, Canada\n"
          f"`!hamilton` - City of Hamilton\n"
          f"`!burlington` - City of Burlington\n"
          f"`!oakville` - Town of Oakville\n"
          f"`!niagara` - Niagara Region\n"
          f"`!brant` - County of Brant\n"
          f"`!haldimand` - Haldimand County\n"
          f"`!norfolk` - Norfolk County\n"
          f"\n"
          f"Categories:\n"
          f"`!chat` - General Pokemon Go discussion\n"
          f"`!exraid` - Hamilton exraids\n"
          f"`!offtopic` - Non-Pokemon Go discussion\n"
          f"`!music` - Music channels\n"
        )
        await self.bot.get_channel(self.bot.configs[str(interaction.guild_id)]['role-channel']).send(welcomeMsg, embed=discord.Embed(description=teamSelectMessage))


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(f'{member.display_name} joined on {member.joined_at}')

    @commands.command(name='top_role', aliases=['toprole'])
    @commands.guild_only()
    async def show_toprole(self, ctx, *, member: discord.Member = None):
        """Simple command which shows the members Top Role."""

        if member is None:
            member = ctx.author

        await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')

    @commands.command(name='nick', aliases=['nickname'])
    @commands.has_permissions(change_nickname=True)
    @commands.guild_only()
    async def update_nickname(self, ctx, *, nickname):
        """Simple command which shows the members Top Role."""
        oldnick = ctx.message.author.display_name

        await ctx.message.author.edit(nick=nickname)
        await ctx.send(f'Your nickname has been changed from `{oldnick}` to `{nickname}`')

    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: discord.Member = None):
        """A simple command which checks a members Guild Permissions.
        If member is not provided, the author will be checked."""

        if not member:
            member = ctx.author

        # Here we check if the value of each permission is True.
        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        # And to make it look nice, we wrap it in an Embed.
        embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))

        # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
        embed.add_field(name='\uFEFF', value=perms)

        await ctx.send(content=None, embed=embed)
        # Thanks to Gio for the Command.

    @commands.command(name='welcome')
    @commands.guild_only()
    async def show_welcome(self, ctx):
        if ctx.channel.id == self.bot.configs[str(ctx.guild.id)]['team-channel'] or ctx.channel.id == 462262985423978496:
            if not ctx.channel.id == 462262985423978496:
                await ctx.channel.purge()
            await ctx.send(f"Welcome to {ctx.guild.name}, please choose a team! If you have any questions tag the `@Mods`.", view=WelcomeView(self.bot))  # Send your message with a button.

    @commands.command(name='hamilton', aliases=['burlington', 'oakville', 'niagara', 'brant', 'haldimand', 'norfolk'])
    @commands.guild_only()
    async def set_region(self, ctx):
        """Set region role"""
        region = discord.utils.get(ctx.guild.roles, name=ctx.invoked_with)
        exraid = discord.utils.get(ctx.guild.roles, name="exraid")
        if ctx.channel.id == self.bot.configs[str(ctx.guild.id)]['role-channel']:
            if region in ctx.author.roles:
                await ctx.author.remove_roles(region, atomic=True)
                await ctx.send(f'Roles removed: ' + region.name)
                if region.name == "hamilton":
                    await ctx.author.remove_roles(exraid, atomic=True)
                    await ctx.send(f'Roles removed: ' + "exraid")
            else:
                await ctx.author.add_roles(region, atomic=True)
                await ctx.send(f'Roles added: ' + region.name)
                if region.name == "hamilton":
                    await ctx.author.add_roles(exraid, atomic=True)
                    await ctx.send(f'Roles added: ' + "exraid")

    @commands.command(name='rh0', aliases=['rh1', 'rh2', 'rh3', 'rh4', 'rh5', 'rh6', 'rh7', 'rh8', 'rh9'])
    @commands.guild_only()
    async def set_group(self, ctx):
        """Set region-notification roles"""
        if ctx.channel.id == self.bot.configs[str(ctx.guild.id)]['role-channel']:
            role = discord.utils.get(ctx.guild.roles, name=ctx.invoked_with)
            if role in ctx.author.roles:
                await ctx.author.remove_roles(role)
                await ctx.send(f'Role removed: ' + role.name)
            else:
                await ctx.author.add_roles(role)
                await ctx.send(f'Role added: ' + role.name)

    @commands.command(name='offtopic', aliases=['music', 'chat', 'exraid'])
    @commands.guild_only()
    async def set_role(self, ctx):
        """Set non-primary roles"""
        if ctx.channel.id == self.bot.configs[str(ctx.guild.id)]['role-channel']:
            role = discord.utils.get(ctx.guild.roles, name=ctx.invoked_with)
            if role in ctx.author.roles:
                await ctx.author.remove_roles(role)
                await ctx.send(f'Role removed: ' + role.name)
            else:
                await ctx.author.add_roles(role)
                await ctx.send(f'Role added: ' + role.name)

    @commands.command(name='hundo', aliases=['nundo', 'pvp'])
    @commands.guild_only()
    async def set_notifications(self, ctx):
        """Set notification roles"""
        if ctx.channel.id == self.bot.configs[str(ctx.guild.id)]['role-channel']:
            role = discord.utils.get(ctx.guild.roles, name=ctx.invoked_with)
            if role in ctx.author.roles:
                await ctx.author.remove_roles(role)
                await ctx.send(f'Role removed: ' + role.name)
            else:
                await ctx.author.add_roles(role)
                await ctx.send(f'Role added: ' + role.name)


async def setup(bot):
    await bot.add_cog(MembersCog(bot))
