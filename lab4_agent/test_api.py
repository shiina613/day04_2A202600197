import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GITHUB_TOKEN")
if not api_key:
    raise ValueError("Missing GITHUB_TOKEN in .env")

client = OpenAI(
	base_url="https://models.inference.ai.azure.com/",
	api_key=api_key,
)

response = client.chat.completions.create(
	messages=[{"role": "user", "content": "Say hello!"}],
	model="gpt-4o",
)

print(response.choices[0].message.content)
