# utils/novita_client.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

NOVITA_API_KEY = os.getenv("NOVITA_OPENAI_API_KEY")
NOVITA_BASE_URL = "https://api.novita.ai/v3/openai"
NOVITA_MODEL = "deepseek/deepseek-r1-0528"

client = OpenAI(
    base_url=NOVITA_BASE_URL,
    api_key=NOVITA_API_KEY,
)

async def call_novita(prompt: str, stream: bool = False, max_tokens: int = 1000) -> str:
    response = client.chat.completions.create(
        model=NOVITA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=stream,
        extra_body={},
    )

    if stream:
        result = ""
        for chunk in response:
            result += chunk.choices[0].delta.content or ""
        return result
    else:
        return response.choices[0].message.content
