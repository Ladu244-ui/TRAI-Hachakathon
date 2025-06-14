from fastapi import FastAPI
from api.routes import router
import os

app = FastAPI(title="Guardrail Sentinel")

app.include_router(router)

if not os.path.exists("reports/generated"):
    os.makedirs("reports/generated")

# Run using `uvicorn main:app --reload`
