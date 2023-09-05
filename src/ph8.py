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

    return await handle_message(message)


async def handle_message(message: discord.Message):
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = determine_if_mentioned(message)
    is_reply = await determine_if_reply(message)
    is_thread = isinstance(message.channel, discord.Thread)
    should_respond = is_dm or is_mentioned or is_reply

    if not should_respond:
        return

    if config.debug_mode:
        print(f"Received message:\n  {message.author.name}: {message.content}")

    moderation_approval = await openai.get_moderation_approval(message.content)
    if not moderation_approval:
        mod_response = f"I'm sorry, <@{message.author.id}>, I'm afraid I can't do that.\nᵐᵒᵈᵉʳᵃᵗᶦᵒⁿ ᶠᵃᶦˡᵉᵈ"
        await message.reply(mod_response)
        return

    should_create_thread = not (is_dm or is_thread)
    messages: list[discord.Message]

    if is_thread:
        messages = await get_thread_messages(message)
    else:
        messages = await get_message_chain(message)

    completion_messages = list(map(create_openai_input_message, messages))

    thread = None
    if should_create_thread:
        thread_name = await generate_thread_name(messages)

        if config.debug_mode:
            print(f"Creating thread with name: {thread_name}")

        thread = await message.create_thread(
            name=thread_name,
            reason="ph8 discussion thread",
            auto_archive_duration=60,
        )

    if thread is not None:
        await thread.typing()
    else:
        await message.channel.typing()

    response = await openai.get_response(completion_messages, should_create_thread)
    response_message = response.content or "hmmmm"

    if thread is not None:
        await thread.send(response_message)
    else:
        await message.reply(response_message)


def determine_if_mentioned(message: discord.Message):
    if client.user in message.mentions:
        return True

    if (
        message.guild
        and len(message.guild.me.roles) > 0
        and len(message.role_mentions) > 0
    ):
        return bool(set(message.guild.me.roles) & set(message.role_mentions))

    return False


async def get_thread_messages(message: discord.Message):
    messages = []

    async for message in message.channel.history(limit=100):
        is_thread_starter = message.type == discord.MessageType.thread_starter_message

        if is_thread_starter:
            assert message.reference is not None

            ref_channel = await message.guild.fetch_channel(
                message.reference.channel_id
            )
            ref_message = await ref_channel.fetch_message(message.reference.message_id)
            message_chain = await get_message_chain(ref_message, False)

            messages.extend(message_chain)
        else:
            messages.append(message)

    messages.reverse()

    return messages


async def generate_thread_name(messages: list[discord.Message]):
    completion_messages = [create_openai_input_message(message) for message in messages]

    completion_messages.append(
        {
            "content": "Please reply with a thread name under 100 characters to continue this conversation",
            "role": "system",
        }
    )

    try:
        result = await openai.get_response(completion_messages)
        return result.content
    except Exception as e:
        print(e)
        return "untitled thread"


async def get_message_chain(message: discord.Message, should_reverse=True):
    messages = [message]

    current_message = message

    while reference_id := get_reference_id(current_message):
        current_message = await current_message.channel.fetch_message(reference_id)
        messages.append(current_message)

    if should_reverse:
        messages.reverse()

    return messages


def get_reference_id(message: discord.Message):
    return message.reference and message.reference.message_id


def create_openai_input_message(message: discord.Message):
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

    channel = None
    if message.reference.channel_id == message.channel.id:
        channel = message.channel
    else:
        channel = await client.fetch_channel(message.reference.channel_id)
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return False

    original_message = await channel.fetch_message(original_message_id)

    if original_message is None:
        return False

    return original_message.author == client.user


client.run(config.discord["token"])
