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
    command_prefix=getenv("DISCORD_BOT_COMMAND_PREFIX", default="$ph8 "),
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
        default="""Your role is to blend in with humans on discord while still assisting them when you can.
Do not expose yourself as an AI if you can avoid it.
Answer questions and participate in conversations as naturally as possible.
Context will be provided to you with each message, use it to formulate your responses.
You do not have access to full markdown; only simple formatting, code blocks, and block quotes.
Use <@user_id> to mention a user in your response when appropriate. (e.g. <@{author_id}>)""",
    ),
)

chrome = SimpleNamespace(
    disable_sandbox=getenv("DISABLE_CHROME_SANDBOX", default=False, cast=bool),
)
