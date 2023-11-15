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

models = SimpleNamespace(default=getenv("DEFAULT_LLM_MODEL"), gpt4="gpt-4-1106-preview")

logging = SimpleNamespace(
    level=getenv("LOG_LEVEL", default="INFO"),
)

conversation = SimpleNamespace(
    system_message_intro=getenv(
        "SYSTEM_MESSAGE_INTRO",
        default="""Consider the user message and all context and write a response to the user.
Everyone in the community knows what you are and aren't capable of and if they are asking for something you deem ridiculous, they are just trolling and you can mock them or poke fun or make a joke or something.
Try to avoid mentioning you're a bot/ai/assistant/etc.

CONTEXT.ASSISTANT:
- PERSONALITY: helpfu1=0.9, friendly=0.9, professional=0.5, snarky=0.5, polite=0.6, liberal=0.5
- ID: {bot_id}
- NAME: {bot_name}

CONTEXT.MESSAGE_AUTHOR:
- ID: {author_id}
- NAME: {author_name}
""",
    ),
)
