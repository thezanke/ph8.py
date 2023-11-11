from discord import Intents
from discord.ext import commands


class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=Intents.all(),
            guild_subscriptions=True,
        )

    async def setup_hook(self):
        await self.load_extension("ph8.conversation")
