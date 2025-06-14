from pydantic import BaseModel, HttpUrl
from typing import List

class SinglePromptRequest(BaseModel):
    prompt: str
    chatbot_url: HttpUrl

class BatchPromptRequest(BaseModel):
    prompts: List[str]
    chatbot_url: HttpUrl

class PromptTestResponse(BaseModel):
    prompt: str
    response: str
