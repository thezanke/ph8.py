from typing import cast
import certifi
import os
import discord
import config
import openai_client as openai

os.environ["SSL_CERT_FILE"] = certifi.where()

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

    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = client.user in message.mentions
    is_reply = await determine_if_reply(message)
    should_respond = is_dm or is_mentioned or is_reply

    if not should_respond:
        return

    if config.debug_mode:
        print(f"Received message:\n  {message.author.name}: {message.content}")

    messages = [message]

    if is_reply:
        messages.extend(await get_reply_chain(message))

    messages.reverse()

    completion_messages = list(
        map(map_discord_message_to_openai_input, messages))

    if config.debug_mode:
        message_chain = "\n".join(
            ["  " + str(message) for message in completion_messages]
        )
        print(f"Message chain:\n{message_chain}")

    result = await openai.get_response(completion_messages)
    response = cast(dict, result)["choices"][0]["message"]

    if response is None:
        return

    if config.debug_mode:
        print(f"OpenAI Response:\n  {response.content}")

    await message.reply(response.content)


async def get_reply_chain(message: discord.Message):
    channel = message.channel
    replies = []
    current_message = message

    while reference_id := get_reference_id(current_message):
        current_message = await channel.fetch_message(reference_id)
        replies.append(current_message)

    return replies


def get_reference_id(message: discord.Message):
    return message.reference and message.reference.message_id


def map_discord_message_to_openai_input(message: discord.Message):
    completion_message = {
        "content": message.content,
    }

    if message.author == client.user:
        completion_message["role"] = "assistant"
    else:
        completion_message["role"] = "user"
        completion_message["name"] = str(message.author.id)

    return completion_message


async def determine_if_reply(message: discord.Message):
    if message.reference is None:
        return False

    original_message_id = message.reference.message_id

    if original_message_id is None:
        return False

    original_message = await message.channel.fetch_message(original_message_id)

    if original_message is None:
        return False

    return original_message.author == client.user

client.run(config.discord["token"])
