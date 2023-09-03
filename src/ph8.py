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
    is_thread = isinstance(message.channel, discord.Thread)
    should_respond = is_dm or is_mentioned or is_reply

    if not should_respond:
        return

    if config.debug_mode:
        print(f"Received message:\n  {message.author.name}: {message.content}")
    should_create_thread = not (is_dm or is_thread)

    messages: list[discord.Message]
    if is_thread:
        messages = await get_thread_messages(message)
    else:
        messages = await get_message_chain(message)

    completion_messages = list(
        map(map_discord_message_to_openai_input, messages))

    thread = None
    if should_create_thread:
        thread_name = await generate_thread_name(messages)
        if config.debug_mode:
            print(f"Creating thread with name: {thread_name}")
        thread = await message.create_thread(name=thread_name)

    response_message = await openai.get_response(completion_messages, is_thread)

    if response_message is None:
        return

    if thread is not None:
        return await thread.send(response_message.content)

    return await message.reply(response_message.content)


async def get_thread_messages(message: discord.Message):
    channel = message.channel
    messages = []
    async for message in channel.history(limit=100):
        messages.append(message)
        
    messages.reverse()
    
    return messages


async def generate_thread_name(messages: list[discord.Message]):
    convo = "\n".join(
        [f"{message.author.name}: {message.content}" for message in messages])

    try:
        result = await openai.get_response(
            [
                {
                    "content": f"Determine a Discord thread name to continue the following conversation:\n\n{convo}",
                    "role": "assistant",
                },
            ]
        )

        return result.content
    except Exception as e:
        print(e)
        return "untitled thread"


async def get_message_chain(message: discord.Message):
    channel = message.channel
    messages = [message]
    
    current_message = message

    while reference_id := get_reference_id(current_message):
        current_message = await channel.fetch_message(reference_id)
        messages.append(current_message)

    messages.reverse()

    return messages


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
