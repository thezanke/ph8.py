from ph8.discord import DiscordBot
import ph8.config
import ph8.chains


def init():
    bot = DiscordBot()
    bot.run(
        token=ph8.config.discord.token,
        log_level=ph8.config.logging.level,
        root_logger=True,
    )


if __name__ == "__main__":
    init()
