import certifi
import os
import discord
import config
import openai_client as openai

os.environ['SSL_CERT_FILE'] = certifi.where()

client = discord.Client(
    intents=discord.Intents.all(),
    guild_subscriptions=True,
)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if config.debug_mode:
        print(f"Received message: {message.content}")

    openai_response = await openai.get_response(message.content)

    await message.channel.send(openai_response)


client.run(config.discord["token"])