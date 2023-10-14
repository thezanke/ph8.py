import dotenv

dotenv.load_dotenv(override=True)

import time
import sys
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

chain = (
    {"text": RunnablePassthrough()}
    | ChatPromptTemplate.from_messages(
        [("system", "You are a joke bot."), ("human", "{text}")]
    )
    | ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9, max_tokens=500, n=1)
    | StrOutputParser()
)


def get_completion(message: str):
    return chain.invoke(message)


message = " ".join(sys.argv[1:])
assert message
print("Message:", message)

start_time = time.perf_counter()
response = get_completion(message)
end_time = time.perf_counter()

print(f"Time taken to get response: {end_time - start_time:0.4f} seconds")
print("Response:", response)
