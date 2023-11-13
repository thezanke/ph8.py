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
    gpt4="gpt-4-1106-preview"
)

logging = SimpleNamespace(
    level=getenv("LOG_LEVEL", default="INFO"),
)
