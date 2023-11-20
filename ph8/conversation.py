from discord.ext import commands
from logging import getLogger
from ph8.cache import LRUCache
import discord
import ph8.chains

logger = getLogger(__name__)


class Conversation(commands.Cog):
    __cache = LRUCache(capacity=500)

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _add_message_to_cache(self, message: discord.Message):
        self.__cache.add(str(message.id), message)

    def _get_message_from_cache(self, message_id: int):
        return self.__cache.get(str(message_id))

    async def _get_referenced_message(self, reference: discord.MessageReference):
        if not reference.message_id:
            return None

        message = self._get_message_from_cache(reference.message_id)

        if message is not None:
            return message

        channel = self.bot.get_channel(reference.channel_id)
        message = await channel.fetch_message(reference.message_id)  # type: ignore

        if message is not None:
            self._add_message_to_cache(message)

        return message

    async def _get_reply_chain(self, message: discord.Message):
        chain: list[discord.Message | discord.DeletedReferencedMessage] = []
        current_message = message

        while reference := current_message.reference:
            current_message = await self._get_referenced_message(reference)

            if current_message is None:
                break

            chain.append(current_message)

        chain.reverse()

        return chain

    async def _before_response_handler(self, message: discord.Message):
        self._add_message_to_cache(message)
        await message.channel.typing()

    async def _response_handler(self, message: discord.Message):
        reply_chain = await self._get_reply_chain(message)

        response = await ph8.chains.ainvoke_conversation_chain(
            bot=self.bot,
            message=message,
            reply_chain=reply_chain,
        )

        await message.reply(response)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.bot.user:
            return

        if message.author.bot:
            return

        if self.bot.user.mentioned_in(message):
            await self._before_response_handler(message)
            await self._response_handler(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Conversation(bot))
