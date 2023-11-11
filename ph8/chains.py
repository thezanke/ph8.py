from textwrap import dedent
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.messages import HumanMessage, SystemMessageChunk
from langchain.schema.output_parser import StrOutputParser
import discord
import discord.ext.commands as commands
import ph8.config


def ainvoke_conversation_chain(
    bot: commands.Bot,
    message: discord.Message,
    reply_chain: list[discord.Message],
):
    if bot.user is None:
        raise ValueError("Bot user is not set")

    input_args = {
        "bot_id": bot.user.id,
        "bot_name": bot.user.display_name,
        "author_id": message.author.id,
        "author_name": message.author.display_name,
        "message_content": message.content,
    }

    system_message = dedent(
        """
            You are a friendly discord denizen.

            ID: {bot_id}
            Name: {bot_name}
            
            A user named {author_name} (ID: {author_id}) has sent you a message.
        """
    )

    if len(reply_chain) > 0:
        system_message += dedent(
            """
                --- Message history ---
                {reply_chain}
            """
        )

        input_args["reply_chain"] = "\n".join([f"{m.author.display_name}: {m.content}" for m in reply_chain])

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_message), "{message_content}"]
    )

    model = ChatOpenAI(model=ph8.config.models.default)

    chain = prompt | model | StrOutputParser()

    return chain.ainvoke(input_args)
