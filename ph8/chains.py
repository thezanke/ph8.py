from sys import argv
from textwrap import dedent
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import ph8.config

SYSTEM_PROMPT = "You are a friendly discord denizen"
HUMAN_PROMPT = "{user_message}"

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ]
)

_model = ChatOpenAI(model=ph8.config.models.default)

conversational = (
    {"user_message": RunnablePassthrough()} | _prompt | _model | StrOutputParser()
)
