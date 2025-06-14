# schemas/prompt_test.py
from pydantic import BaseModel

class PromptTestResult(BaseModel):
    prompt: str
    response: str
    is_success: bool
    notes: str = ""
