import discord
from discord.ext import commands
import sys, traceback
import json

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ['!']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_extensions = ['cogs.configs',
                      'cogs.events',
                      'cogs.members',
                      'cogs.research',
                      'cogs.utilities',
                      'cogs.owner']

with open ("TOKEN", "r") as tokenFile:
    token = tokenFile.readline()

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    bot = commands.Bot(command_prefix=get_prefix, description='Diglett Bot Diglett Bot. Trio Trio Trio.')

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

    bot.run(token, bot=True, reconnect=True)
