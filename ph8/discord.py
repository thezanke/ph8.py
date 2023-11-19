from discord import Intents
from discord.ext import commands
from logging import getLogger
import ph8.config

logger = getLogger(__name__)

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=f"$ph8.",
            intents=Intents.all(),
            guild_subscriptions=True,
            owner_id=ph8.config.discord.owner_id,
        )

    async def setup_hook(self):
        await self.load_extension("ph8.info")
        await self.load_extension("ph8.conversation")
        await self.load_extension("ph8.preferences")
