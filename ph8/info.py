from datetime import datetime, timedelta
from logging import getLogger
from discord.ext import commands

start_time = datetime.utcnow()
logger = getLogger(__name__)


class Information(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def strfdelta(self, tdelta: timedelta):
        days = tdelta.days
        hours, rem = divmod(tdelta.seconds, 3600)
        minutes, seconds = divmod(rem, 60)

        parts = []
        if days:
            parts.append(f"{days} day{'s' if days > 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")

        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        return ", ".join(parts)

    @commands.command()
    async def uptime(self, ctx: commands.Context):
        uptime = datetime.utcnow() - start_time
        uptime_str = self.strfdelta(uptime)
        await ctx.reply(
            f"```⏲️ {uptime_str} elapsed since starting at {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC.```"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Information(bot))
