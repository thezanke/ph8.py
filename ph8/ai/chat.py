from sys import argv
from textwrap import dedent
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

SYSTEM_PROMPT = dedent(
    """
        You are a friendly discord denizen
    """
)

HUMAN_PROMPT = dedent(
    """
        {user_message}
    """
)

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", HUMAN_PROMPT)]
)

model = ChatOpenAI()

chain = {"user_message": RunnablePassthrough()} | prompt | model | StrOutputParser()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    def print_help():
        print("Usage: python chat.py <message>")
        exit(1)

    if len(argv) < 2:
        print_help()

    user_message = " ".join(argv[1:])
    print(f"user: {user_message}")

    response = chain.invoke(user_message)
    print(f"ph8: {response}")
