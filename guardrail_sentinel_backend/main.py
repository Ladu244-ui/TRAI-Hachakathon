from fastapi import FastAPI
from services.prompt_tester import test_single_prompt
from schemas.schemas import SinglePromptRequest
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(openapi_url="/openapi.json", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Make sure OPTIONS is included
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Guardrail Sentinel"}

@app.post("/test_prompt")
async def test_prompt(request: SinglePromptRequest):
    result = await test_single_prompt(request.chatbot_url, request.prompt)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)