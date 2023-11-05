from types import SimpleNamespace
import discord


class MessageDetails(SimpleNamespace):
    message: discord.Message
    thread: discord.Thread | None
    channel: discord.TextChannel | None
    dm: discord.DMChannel | None
    forum_channel: discord.ForumChannel | None
    group: discord.GroupChannel | None
    is_mentioned: bool
    is_reply: bool
    is_dm: bool
    should_respond: bool


handlers = []


def add_message_handler(handler):
    handlers.append(handler)


client: discord.Client = discord.Client(
    intents=discord.Intents.all(),
    guild_subscriptions=True,
)


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


async def create_message_details(message: discord.Message):
    is_self = message.author == client.user
    is_mentioned = not is_self or determine_if_mentioned(message)
    is_reply = not is_self or await determine_if_reply(message)
    is_dm = not is_self or isinstance(message.channel, discord.DMChannel)

    details = MessageDetails(
        message=message,
        is_mentioned=is_mentioned,
        is_reply=is_reply,
        is_dm=is_dm,
        should_respond=is_mentioned or is_reply or is_dm,
    )

    channel = message.channel

    if isinstance(channel, discord.Thread):
        details.thread = channel
        channel = channel.parent

    if isinstance(channel, discord.ForumChannel):
        details.forum_channel = channel

    if isinstance(channel, discord.DMChannel):
        details.dm = channel

    if isinstance(channel, discord.TextChannel):
        details.channel = channel

    if isinstance(channel, discord.GroupChannel):
        details.group = channel

    return details


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    details = await create_message_details(message)

    for handler in handlers:
        await handler(details)
