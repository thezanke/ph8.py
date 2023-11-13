from logging import getLogger
from discord import Intents
from discord.ext import commands
import ph8.config

logger = getLogger(__name__)

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="$ph8 ",
            help_command=None,
            intents=Intents.all(),
            guild_subscriptions=True,
            owner_id=ph8.config.discord.owner_id
        )

    async def setup_hook(self):
        await self.load_extension("ph8.conversation")
