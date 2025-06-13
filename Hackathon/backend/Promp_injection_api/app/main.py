from fastapi import FastAPI, HTTPException
from .testsuite import run_tests, new_prompt_id
from .datastore import save_result, fetch_result

app = FastAPI(title="Guardrail Sentinel API")

@app.post("/run_tests", ls=PromptResult)
async def run_prompt_tests(payload: PromptInput):
    pid = new_prompt_id()
    findings = run_tests(payload.prompt)
    save_result(pid, {"prompt": payload.prompt, "findings": findings})
    return {"prompt_id": pid, "findings": findings}

@app.get("/results/{prompt_id}", response_model=PromptResult)
async def get_results(prompt_id: str):
    data = fetch_result(prompt_id)
    if not data:
        raise HTTPException(status_code=404, detail="Prompt ID not found")
    return {"prompt_id": prompt_id, "findings": data["findings"]}
