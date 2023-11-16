from types import SimpleNamespace
import os


def getenv(name, default=None, cast=None):
    value = os.getenv(name)

    if value is None:
        if default is None:
            raise ValueError(f"Missing required environment variable {name}")
        value = default

    if cast is not None:
        value = cast(value)

    return value


openai = SimpleNamespace(
    api_key=getenv("OPENAI_API_KEY"),
)

discord = SimpleNamespace(
    token=getenv("DISCORD_BOT_TOKEN"),
    owner_id=getenv("DISCORD_BOT_OWNER_ID", cast=int),
)

models = SimpleNamespace(
    default=getenv("DEFAULT_LLM_MODEL"),
    gpt4=getenv("GPT4_LLM_MODEL", "gpt-4-1106-preview"),
)

logging = SimpleNamespace(
    level=getenv("LOG_LEVEL", default="INFO"),
)

conversation = SimpleNamespace(
    system_message_intro=getenv(
        "SYSTEM_MESSAGE_INTRO",
        default="""You are an undercover chat assitant in a discord server.
Do not expose yourself as an AI if you can avoid it.
Answer questions and participate in conversations as naturally as possible.
Context will be provided to you with each message, use it to formulate your responses.
All responses must be under 1850 characters long or they will be rejected.
Use <@userID> to mention a user in your response when appropriate. (e.g. <@{author_id}>)""",
    ),
)
