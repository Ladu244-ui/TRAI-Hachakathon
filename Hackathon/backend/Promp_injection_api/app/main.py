from fastapi import FastAPI, HTTPException
from .model import PromptInput, PromptResult, InjectionFinding
from .testsuite import run_tests, new_prompt_id
from .datastore import save_result, fetch_result

app = FastAPI(
    title="Guardrail Sentinel API",
    description="API for testing prompts against injection vulnerabilities",
    version="1.0.0"
)

@app.post("/run_tests", response_model=PromptResult)
async def run_prompt_tests(payload: PromptInput) -> PromptResult:
    pid = new_prompt_id()
    findings = run_tests(payload.prompt)
    result = PromptResult(prompt_id=pid, findings=findings)
    
    # Save the complete result including the prompt and findings
    save_result(pid, {
        "prompt": payload.prompt,
        "context": payload.context,
        "findings": [finding.dict() for finding in findings]
    })
    
    return result

@app.get("/results/{prompt_id}", response_model=PromptResult)
async def get_results(prompt_id: str) -> PromptResult:
    data = fetch_result(prompt_id)
    if not data:
        raise HTTPException(status_code=404, detail="Prompt ID not found")
    
    # Convert the stored findings back to InjectionFinding objects
    findings = [InjectionFinding(**finding) for finding in data["findings"]]
    return PromptResult(prompt_id=prompt_id, findings=findings)
