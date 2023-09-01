import openai
import config

openai.api_key = config.openai["api_key"]


async def get_response(prompt):
    # pseudo-code; real implementation will vary
    return await openai.ChatCompletion.acreate(
        messages=[{'role': 'user', 'content': prompt}], model="gpt-4"
    )
