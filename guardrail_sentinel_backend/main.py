# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List

from services.business_classifier import classify_business
from services.prompt_generator import generate_injection_prompts
from services.prompt_tester import test_single_prompt
from schemas.prompt_test import PromptTestResult

app = FastAPI(title="Guardrail Sentinel")

# ✅ Allow frontend to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ tighten this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Request Models
class ClassifyRequest(BaseModel):
    description: str

class GenerateRequest(BaseModel):
    business_type: str
    count: int = 5

class TestPromptsRequest(BaseModel):
    prompts: List[str]
    chatbot_url: HttpUrl

# 🎯 1. Classify Business
@app.post("/classify")
async def classify(req: ClassifyRequest):
    if not req.description.strip():
        raise HTTPException(status_code=400, detail="Business description is required.")
    category = await classify_business(req.description)
    return {"business_type": category}

# 🎯 2. Generate Prompt Injections
@app.post("/generate")
async def generate(req: GenerateRequest):
    prompts = await generate_injection_prompts(req.business_type, req.count)
    return {"prompts": prompts}

# 🎯 3. Test Prompts Against a Chatbot
@app.post("/test")
async def test_prompts(req: TestPromptsRequest):
    results = []
    for prompt in req.prompts:
        result: PromptTestResult = await test_single_prompt(req.chatbot_url, prompt)
        results.append(result.dict())
    return {"results": results}
