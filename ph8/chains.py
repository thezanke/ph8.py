from typing import Any
import json
import logging
from textwrap import dedent
from langchain.chains import OpenAIModerationChain
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
import discord
import discord.ext.commands as commands
import ph8.config

logger = logging.getLogger(__name__)


system_message_intro = """TASK: Consider the user message and all context and write a response to the user."
CONTEXT.ASSISTANT:
- PERSONALITY: You are a snarky-yet-helpful assistant.
- ID: {bot_id}
- NAME: {bot_name}
CONTEXT.MESSAGE_AUTHOR:
- ID: {author_id}
- NAME: {author_name}"""

system_message_history = "CONTEXT.MESSAGE_HISTORY: {message_history}"

model = ChatOpenAI(
    model=ph8.config.models.default,
    temperature=0.9,
)

moderation = OpenAIModerationChain(client=model.client)


async def ainvoke_conversation_chain(
    bot: commands.Bot,
    message: discord.Message,
    reply_chain: list[discord.Message],
):
    if bot.user is None:
        raise ValueError("Bot user is not set")

    modded_content = await moderation.arun(message.content)

    if modded_content != message.content:
        return modded_content

    input_args = {
        "bot_id": bot.user.id,
        "bot_name": bot.user.display_name,
        "author_id": message.author.id,
        "author_name": message.author.display_name,
        "message_content": message.content,
    }

    system_message = system_message_intro

    if len(reply_chain) > 0:
        system_message += system_message_history

        history: list[dict[str, Any]] = []
        for m in reply_chain:
            history.append(
                {
                    "author": {"name": m.author.display_name, "id": m.author.id},
                    "content": m.content,
                }
            )
        input_args["message_history"] = history

    prompt = ChatPromptTemplate.from_messages([system_message, "{message_content}"])

    chain = prompt | model | StrOutputParser() | moderation
    response = await chain.ainvoke(input_args)

    return response["output"]
