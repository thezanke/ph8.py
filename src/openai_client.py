from typing import cast
import openai
import config

openai.api_key = config.openai["api_key"]


async def get_response(messages, is_thread=False):

    if config.debug_mode:
        message_chain = "\n".join(
            ["  " + str(message) for message in messages]
        )
        print(f"OpenAI request, message chain:\n{message_chain}")

    messages_to_send = []
    if is_thread:
        messages_to_send.append(
            {"role": "system", "content": "make sure you reply to the user"})
    messages_to_send.extend(messages)

    response = await openai.ChatCompletion.acreate(
        messages=messages_to_send,
        model="gpt-4",
    )

    response_message = cast(dict, response)["choices"][0]["message"]

    if config.debug_mode:
        print(f"OpenAI Response:\n  {response_message}")

    return response_message
