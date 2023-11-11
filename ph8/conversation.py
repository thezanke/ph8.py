from logging import getLogger
import discord
from discord.ext import commands
from ph8.chains import conversational


logger = getLogger(__name__)


class ConversationCog(commands.Cog, name="Conversation"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _handle_conversation_message(self, message: discord.Message):
        response = await conversational.ainvoke(message.content)
        await message.reply(response)

    async def _is_conversation_response(self, message: discord.Message):
        if message.reference is None:
            return False

        if message.reference.resolved is None:
            return False

        if not isinstance(message.reference.resolved, discord.Message):
            return False

        if not isinstance(self.bot.user, discord.User):
            return False

        return message.reference.resolved.author.bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if not isinstance(error, commands.CommandNotFound):
            raise error

        if self._is_conversation_response(ctx.message):
            return

        logger.info("Command not found, conversing instead...")

        await self._handle_conversation_message(ctx.message)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user and self.bot.user.mentioned_in(message):
            return

        if self._is_conversation_response(message):
            await self._handle_conversation_message(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(ConversationCog(bot))
