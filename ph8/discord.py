import discord

handlers = []


def add_message_handler(handler):
    handlers.append(handler)


client: discord.Client = discord.Client(
    intents=discord.Intents.all(),
    guild_subscriptions=True,
)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    for handler in handlers:
        await handler(message)