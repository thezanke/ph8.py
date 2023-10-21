from bs4 import BeautifulSoup
from ph8.openai import openai_client, OpenAICompletionMessage
from textwrap import dedent
from typing import NotRequired, TypedDict
import certifi
import discord
import os
import ph8.config
import requests

os.environ["SSL_CERT_FILE"] = certifi.where()

client: discord.Client = discord.Client(
    intents=discord.Intents.all(),
    guild_subscriptions=True,
)


async def get_content_from_url(parameters: dict[str, str]):
    url = parameters["url"]
    response = requests.get(url, headers={"User-Agent": ""})
    soup = BeautifulSoup(response.content, "html.parser")

    return soup.text


openai_client.register_function(
    name="get_content_from_url",
    description="Get the text content from a URL",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to get the content from",
            },
        },
        "required": ["url"],
    },
    handler=get_content_from_url,
)


class SendReplyParams(TypedDict):
    message_id: int
    channel_id: int
    reply: str


async def send_reply(parameters: SendReplyParams):
    channel_id = parameters["channel_id"]
    channel = await client.fetch_channel(channel_id)

    assert isinstance(channel, (discord.TextChannel, discord.Thread, discord.DMChannel))

    message_id = parameters["message_id"]
    message = await channel.fetch_message(message_id)

    reply_text = parameters["reply"]

    reply = await message.reply(reply_text)

    return create_openai_input_message(reply)


class CompleteRequestParams(TypedDict):
    message_id: int
    channel_id: int
    reason: NotRequired[str]


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

    if ph8.config.debug_mode:
        print(f"Received message:\n  {message.author.name}: {message.content}")

    if message.author.bot:
        if ph8.config.debug_mode:
            print(f"Ignoring message from bot: {message.author.name}")
        return

    moderation_approval = await openai_client.get_moderation_approval(message.content)
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

    thread = None
    if should_create_thread:
        thread_name = await generate_thread_name(messages)

        if ph8.config.debug_mode:
            print(f"Creating thread with name: {thread_name}")

        thread = await message.create_thread(
            name=thread_name, reason="ph8 discussion thread", auto_archive_duration=60
        )

    if thread is not None:
        await thread.typing()
    else:
        await message.channel.typing()

    completion_messages: list[OpenAICompletionMessage] = [
        {
            "content": create_system_message(message, messages, thread),
            "role": "system",
        },
    ]

    completion_messages.extend(
        create_openai_input_message(message) for message in messages
    )

    response = await openai_client.get_response(completion_messages)

    while response["finish_reason"] == "stop":
        response_message = response["message"]

        if ph8.config.debug_mode:
            print(f"Non-functional response received:\n  {response_message}")

        completion_messages.append(response_message)
        completion_messages.append(
            {
                "content": "Please call `send_reply` or `complete_request` using your response to continue.",
                "role": "system",
            }
        )

        response = await openai_client.get_response(completion_messages)

    # if thread is not None:
    #     await thread.send(response_message)
    # else:
    #     await message.reply(response_message)


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


def create_system_message(
    message: discord.Message,
    messages: list[discord.Message],
    thread: discord.Thread | None = None,
):
    details = [
        "You are a multi-user chat assistant.",
        "You are able to be tagged by any users, by name or role, and can reply in DMs.",
        f"Your details: {str(getattr(message.channel, 'me', client.user))}",
        "Only call the functions you have been provided.",
        "You must call `send_reply` to send a reply.",
        "You must call `request_complete` when you are done handling a request.",
    ]

    if message.guild:
        details.append(f"Server Name: {message.guild.name}.")

    if isinstance(message.channel, discord.TextChannel):
        details.append(f"Channel Name: {message.channel.name}.")

    if not thread and isinstance(message.channel, discord.Thread):
        thread = message.channel

    if thread:
        if thread.parent:
            details.append(f'Channel Name: "{thread.parent.name}".')
        details.append(f'Thread Title: "{thread.name}".')

    if isinstance(message.channel, discord.DMChannel) and message.channel.recipient:
        details.append(
            f"DMing With: {message.channel.recipient.name} (ID: {message.channel.recipient.id})."
        )

    participants = getattr(
        message.channel, "members", set([message.author for message in messages])
    )

    participants_details = {p.id: str(p) for p in participants}

    details.append(f"Participants: {participants_details}.")

    details.append(
        f'Use <@participant.id> to mention/tag participants, example: "<@1111222233334444555> I hope you\'ve had a good day!".'
    )

    return "\n".join(details)


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
    thread_str = "\n".join(
        [f"\t{get_discord_message_details(message)}" for message in messages]
    )

    completion_messages: list[OpenAICompletionMessage] = [
        {
            "content": dedent(
                f"""
                Return a funny title for this thread:
                {thread_str}
                
                Requirements:
                * Must be between 1 and 100 characters.
                * Must be clever or funny.
                * Must be titlecased. Must not be quoted.
                * Must not contain any user IDs or mentions."""
            ),
            "role": "system",
        }
    ]

    try:
        result = await openai_client.get_response(completion_messages)
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


def create_openai_input_message(message: discord.Message) -> OpenAICompletionMessage:
    if message.author == client.user:
        return {
            "role": "assistant",
            "content": message.content,
        }
    else:
        return {
            "role": "user",
            "content": str(get_discord_message_details(message)),
        }


def get_discord_message_details(message: discord.Message):
    return {
        "id": message.id,
        "content": message.content,
        "author": get_user_details(message.author),
        "attachments": [get_attachment_details(a) for a in message.attachments],
        "embeds": [get_embed_details(e) for e in message.embeds],
    }


def get_embed_details(embed: discord.Embed):
    return {
        "title": embed.title,
        "description": embed.description,
        "url": embed.url,
        "type": embed.type,
    }


def get_attachment_details(attachment: discord.Attachment):
    return {
        "url": attachment.url,
        "filename": attachment.filename,
        "size": attachment.size,
        "content_type": attachment.content_type,
        "description": attachment.description,
    }


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


PARTICIPANT_KEYS = ("id", "name", "bot", "nick")


def get_user_details(
    participant: discord.User
    | discord.Member
    | discord.ThreadMember
    | discord.ClientUser
    | None,
):
    return {key: getattr(participant, key, "N/A") for key in PARTICIPANT_KEYS}


def init():
    client.run(ph8.config.discord["token"])
