import discord
from discord.ext import commands


class DiglettBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # Requires setting in Bot settings on discord developer site
        intents.message_content = True

        super().__init__(command_prefix='!', description='Diglett Bot Diglett Bot. Trio Trio Trio.', intents=intents)

        self.initial_extensions = [
            'cogs.configs',
            'cogs.events',
            'cogs.members',
            'cogs.research',
            'cogs.utilities',
            'cogs.owner',
        ]

    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)

    async def close(self):
        await super().close()


if __name__ == '__main__':
    with open("TOKEN", "r") as tokenFile:
        token = tokenFile.readline()

    bot = DiglettBot()
    bot.run(token, reconnect=True)
