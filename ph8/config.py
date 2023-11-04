from types import SimpleNamespace
from dotenv import load_dotenv
import os


def getenv(name, default=None, cast=None):
    value = os.getenv(name)
    if value is None:
        if default is not None:
            value = default
        else:
            raise ValueError(f"Missing required environment variable {name}")
    if cast is not None:
        value = cast(value)
    return value


load_dotenv()


openai = SimpleNamespace(
    api_key=getenv("OPENAI_API_KEY"),
)

discord = SimpleNamespace(
    token=getenv("DISCORD_BOT_TOKEN"),
)

models = SimpleNamespace(
    default=getenv("DEFAULT_LLM_MODEL"),
)

debug_mode = getenv("DEBUG", default=False, cast=bool)
