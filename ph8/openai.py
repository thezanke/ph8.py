from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import cast
from typing import NotRequired, TypedDict
import json
import openai
import ph8.config as config

openai.api_key = config.openai["api_key"]


class OpenAICompletionMessage(TypedDict):
    content: str
    role: str
    name: NotRequired[str]


class OpenAIClient:
    functions = []
    func_register = {}

    def register_function(
        self,
        name: str,
        description: str,
        parameters: dict[str, str | dict[str, dict[str, str]] | list[str]],
        handler,
    ):
        self.functions.append(
            {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        )
        self.func_register[name] = handler

    async def get_summary(
        self,
        input: str,
        model="gpt-3.5-turbo-16k-0613",
    ):
        response = await openai.ChatCompletion.acreate(
            messages=[
                {
                    "content": """
                        Summarize extracted web page text.
                        If response is a paywall, http error, etc, return a helpful message for the user.""",
                    "role": "system",
                },
                {"content": input, "role": "user"},
            ],
            model=model,
            temperature=0.5,
        )

        response_message = cast(dict, response)["choices"][0]["message"]

        return response_message.content

    async def get_response(
        self,
        messages: list[OpenAICompletionMessage],
        model="gpt-3.5-turbo-16k-0613",
        temperature=0.9,
    ):
        if config.debug_mode:
            message_chain = "\n".join(map(lambda x: f"  {x}", messages))
            print(f"OpenAI request, message chain:\n{message_chain}")

        req_args = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
        }

        # Add functions if they exist
        if len(self.functions) > 0:
            req_args["functions"] = self.functions

        response = await openai.ChatCompletion.acreate(**req_args)

        full_response = cast(dict, response)["choices"][0]
        response_message = full_response["message"]

        if config.debug_mode:
            print(f"OpenAI Response: {full_response}")

        if full_response["finish_reason"] == "function_call":
            if config.debug_mode:
                print(f"OpenAI function call: {response_message['function_call']}")

            handler_name = response_message["function_call"]["name"]
            handler_parameters = json.loads(
                response_message["function_call"]["arguments"]
            )
            handler = self.func_register[handler_name]

            handler_response = await handler(handler_parameters)

            messages.append(
                {
                    "content": handler_response,
                    "role": "function",
                    "name": handler_name,
                }
            )

            if handler_name != "complete_request":
                return await self.get_response(
                    messages=messages, model=model, temperature=temperature
                )

        return full_response

    async def get_moderation_approval(self, message_content: str):
        if config.debug_mode:
            print(f"OpenAI moderation requested for: {message_content}")

        response = await openai.Moderation.acreate(input=message_content)

        if config.debug_mode:
            print(f"OpenAI moderation response: {response}")

        flagged: bool = cast(dict, response)["results"][0]["flagged"] or False

        if config.debug_mode:
            print(f"OpenAI moderation flagged: {flagged}")

        return not flagged


openai_client = OpenAIClient()
