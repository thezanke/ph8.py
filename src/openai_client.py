from types import SimpleNamespace
from typing import cast
from bs4 import BeautifulSoup
import requests
import openai
import config

openai.api_key = config.openai["api_key"]


functions = [
    {
        "name": "get_content_from_url",
        "description": "Get the text content from a URL",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to get the content from",
                },
            },
            "required": ["url"],
        },
    }
]


async def get_content_from_url(params: dict[str, str]):
    url = params["url"]
    respone = requests.get(url)
    soup = BeautifulSoup(respone.content, "html.parser")
    return soup.text


func_register = {
    "get_content_from_url": get_content_from_url,
}


async def get_response(
    messages: list[dict[str, str]],
    model="gpt-3.5-turbo-16k-0613",
    temperature=0.9,
):
    if config.debug_mode:
        message_chain = "\n".join(map(lambda x: f"  {x}", messages))
        print(f"OpenAI request, message chain:\n{message_chain}")

    response = await openai.ChatCompletion.acreate(
        messages=messages,
        model=model,
        temperature=temperature,
        functions=functions,
    )

    response_message = cast(dict, response)["choices"][0]["message"]

    if config.debug_mode:
        print(f"OpenAI Response: {response_message}")

    if response_message["function_call"] is not None:
        function_name = response_message["function_call"]["function"]
        function_params = response_message["function_call"]["parameters"]
        function = func_register[function_name]
        function_response = await function(function_params)
        fn_response_message = { "content": function_response, "" }

    return response_message


async def get_moderation_approval(message_content: str):
    if config.debug_mode:
        print(f"OpenAI moderation requested for: {message_content}")

    response = await openai.Moderation.acreate(input=message_content)

    if config.debug_mode:
        print(f"OpenAI moderation response: {response}")

    flagged: bool = cast(dict, response)["results"][0]["flagged"] or False

    if config.debug_mode:
        print(f"OpenAI moderation flagged: {flagged}")

    return not flagged
