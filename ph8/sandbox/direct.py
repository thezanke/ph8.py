import dotenv
import time

dotenv.load_dotenv(override=True)

import os
import sys
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_completion(message: str):
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    temperature=0.9,
    max_tokens=500,
    n=1,
    messages=[
      {"role": "system", "content": "You are a joke bot."},
      {"role": "user", "content": message},
    ],
  )

  return completion.choices[0].message["content"]  # type: ignore


# get `message` from argv
message = " ".join(sys.argv[1:])
assert message
print("Message:", message)

start_time = time.perf_counter()
response = get_completion(message)
end_time = time.perf_counter()

print(f"Time taken to get response: {end_time - start_time:0.4f} seconds")
print("Response:", response)
