from dotenv import load_dotenv
import os

required_vars = ["DISCORD_BOT_TOKEN", "OPENAI_API_KEY"]


def validate_env():
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            raise EnvironmentError(
                f"Environment variable {var} is missing or set to None."
            )


load_dotenv()
validate_env()

openai = {
    "api_key": str(os.getenv("OPENAI_API_KEY")),
}

discord = {
    "token": str(os.getenv("DISCORD_BOT_TOKEN")),
}

debug_mode = bool(os.getenv("DEBUG"))
