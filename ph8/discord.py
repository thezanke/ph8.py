from discord import Intents
from discord.ext import commands
from logging import getLogger
import ph8.config

logger = getLogger(__name__)


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, "on_error"):
            return

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, commands.CommandNotFound):
            await ctx.message.add_reaction("❌")
            await ctx.reply(
                "```"
                + f"❌ {error}.\n\n"
                + f"HINT: Use `{ph8.config.discord.command_prefix}help` for a list of commands."
                + "```"
            )


class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=ph8.config.discord.command_prefix,
            intents=Intents.all(),
            guild_subscriptions=True,
            owner_id=ph8.config.discord.owner_id,
        )

    async def setup_hook(self):
        await self.add_cog(CommandErrorHandler(self))
        await self.load_extension("ph8.info")
        await self.load_extension("ph8.conversation")
        await self.load_extension("ph8.preferences")
