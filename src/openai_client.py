import openai
import config

openai.api_key = config.openai["api_key"]

async def get_response(messages):
    return await openai.ChatCompletion.acreate(
        messages=messages,
        model="gpt-4",
    )
