from logging import getLogger
from discord.ext import commands
from ph8.chains import conversational


logger = getLogger(__name__)


class ConversationCog(commands.Cog, name="Conversation"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if not isinstance(error, commands.CommandNotFound):
            raise error

        logger.info("Command not found, conversing instead...")

        response = await conversational.ainvoke(ctx.message.content)
        await ctx.message.reply(response)


async def setup(bot: commands.Bot):
    await bot.add_cog(ConversationCog(bot))
