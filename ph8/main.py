import discord
import ph8.discord
import ph8.config
import ph8.ai.chat


async def handle_discord_message(message: discord.Message):
    print(f"Received message: {message.content}")
    response = ph8.ai.chat.chain.invoke(message.content)
    print(f"Response: {response}")
    await message.reply(response)


def init():
    ph8.discord.add_message_handler(handle_discord_message)
    ph8.discord.client.run(ph8.config.discord["token"])
