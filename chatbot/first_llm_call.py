import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    temperature=1,
    messages=[
        {"role":"system","content":"You are a helpful bank assistant.Keep answers short."},
        {"role":"user","content":"What is a fixed deposit?"},
        {"role":"user","content":"What is a fixed deposit?"},
        {"role":"user","content":"What is a fixed deposit?"}
    ]
)

print(response.choices[0].message.content)