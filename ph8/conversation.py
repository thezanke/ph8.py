from logging import getLogger
import discord
from discord.ext import commands
import ph8.chains

logger = getLogger(__name__)


class ConversationCog(commands.Cog, name="Conversation"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def __handle_conversation_message(
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

    async def __get_reply_chain(self, message: discord.Message):
        chain = []
        current_message = message

        while reference := current_message.reference:
            if not reference.message_id:
                break
            current_message = (
                reference.cached_message
                or await current_message.channel.fetch_message(reference.message_id)
            )
            chain.append(current_message)

        chain.reverse()

        return chain

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not self.bot.user:
            return

        if self.bot.user.mentioned_in(message):
            reply_chain = await self.__get_reply_chain(message)

            await self.__handle_conversation_message(
                message=message,
                reply_chain=reply_chain,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ConversationCog(bot))
