from langchain.chains import OpenAIModerationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from langchain.agents import Tool
from langchain.tools.render import format_tool_to_openai_function
from ph8.preferences import Preferences
import discord
import discord.ext.commands as commands
import logging
import ph8.config

logger = logging.getLogger(__name__)

async def ainvoke_conversation_chain(
    bot: commands.Bot,
    message: discord.Message,
    reply_chain: list[discord.Message | discord.DeletedReferencedMessage],
):
    if bot.user is None:
        raise ValueError("Bot user is not set")

    preferences: Preferences = bot.get_cog("Preferences")  # type: ignore
    if preferences is None:
        raise ValueError("Preferences cog is not loaded")

    model_name = preferences.get_user_pref(message.author.id, "model_name")

    llm = ChatOpenAI(model=model_name, temperature=0.7, max_tokens=420)
    moderation = OpenAIModerationChain(client=llm.client)

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

    messages = [
        ("system", ph8.config.conversation.system_message_intro),
        ("system", "CONTEXT.ASSISTANT:\n\n* NAME: {bot_name}\n* ID: {bot_id}"),
    ]

    if len(reply_chain):
        messages.append(("system", "CONTEXT.MESSAGE_HISTORY:\n\n{message_history}"))

        history: list[str] = []

        for m in reply_chain:
            if isinstance(m, discord.DeletedReferencedMessage):
                history.append("<deleted message>")
                continue

            history.append(f"{m.author.display_name} (ID: {m.author.id}): {m.content}")
        input_args["message_history"] = "\n".join(history)

    messages.append(
        (
            "system",
            "CONTEXT.MESSAGE_AUTHOR:\n\n* Name:{author_name}\n* ID: {author_id}",
        )
    )
    messages.append(("human", "{message_content}"))
    messages.append(MessagesPlaceholder(variable_name="agent_scratchpad"))

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm | StrOutputParser() | moderation
    response = await chain.ainvoke(input_args)

    return response["output"]
