from logging import getLogger
import discord
from discord.ext import commands
import ph8.chains

logger = getLogger(__name__)


def get_reference_id(message: discord.Message):
    return message.reference and message.reference.message_id


class ConversationCog(commands.Cog, name="Conversation"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _handle_conversation_message(
        self,
        message: discord.Message,
        reply_chain: list[discord.Message],
    ):
        response = await ph8.chains.ainvoke_conversation_chain(
            bot=self.bot,
            message=message,
            reply_chain=reply_chain,
        )

        await message.reply(response)

    async def _get_reply_chain(self, message: discord.Message):
        chain = []
        current_message = message

        while reference_id := get_reference_id(current_message):
            current_message = await current_message.channel.fetch_message(reference_id)
            chain.append(current_message)

        chain.reverse()

        return chain

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user and self.bot.user.mentioned_in(message):
            reply_chain = await self._get_reply_chain(message)

            await self._handle_conversation_message(
                message=message,
                reply_chain=reply_chain,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ConversationCog(bot))
