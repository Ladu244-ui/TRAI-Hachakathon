from fastapi import FastAPI, HTTPException
from app.model import PromptInput, PromptResult, InjectionFinding
from app.utils import new_prompt_id, run_tests, save_result, fetch_result
import uvicorn   # run the app locally
from typing import Dict, Any

# create the FastAPI App
app = FastAPI(
    title="Guardrail Sentinel API",
    description="API for testing prompts against security guardrails",
    version="1.0.0",
    docs_url="/docs",   # will serve the interactive Swagger UI
    redoc_url="/redoc"   # will serve the ReDoc documentation
)

@app.post(
    "/run_tests",
    response_model=PromptResult,
    summary="Run Prompt Security Tests",
    description="Analyzes a given prompt for potential security vulnerabilities and injection risks",
    response_description="Returns the test findings along with a unique prompt ID"
)

# Accepts a prompt from the user
async def run_prompt_tests(payload: PromptInput):  
    """Run security tests on the provided prompt.
    
    Args:
        payload (PromptInput): The prompt to be tested
        
    Returns:
        PromptResult: Test findings and prompt ID
        
    Raises:
        HTTPException: If the test execution fails
    """
    try:
        pid = new_prompt_id()
        test_results = run_tests(payload.prompt)
        save_result(pid, {"prompt": payload.prompt, "findings": test_results["findings"]})
        return PromptResult(
            prompt_id=pid,
            findings=test_results["findings"],
            risk_score=test_results["risk_score"],
            total_findings=test_results["total_findings"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/results/{prompt_id}",
    response_model=PromptResult,
    summary="Get Test Results",
    description="Retrieves the test results for a specific prompt ID",
    response_description="Returns the findings associated with the given prompt ID"
)
async def get_results(prompt_id: str):
    """Retrieve test results for a specific prompt ID.
    
    Args:
        prompt_id (str): The unique identifier of the prompt test
        
    Returns:
        Dict[str, Any]: Test findings for the given prompt ID
        
    Raises:
        HTTPException: If the prompt ID is not found
    """
    data = fetch_result(prompt_id)
    if not data:
        raise HTTPException(status_code=404, detail="Prompt ID not found")
    return PromptResult(
        prompt_id=prompt_id,
        findings=data["findings"],
        risk_score=data.get("risk_score", 0.0),
        total_findings=len(data["findings"])
    )
@app.get("/")
def home():
    return {"message": "Welcome to the Guardrail Sentinel API. Visit /docs to test the endpoints."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 