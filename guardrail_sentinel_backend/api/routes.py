from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import sys
import os
from schemas.schemas import SinglePromptRequest
from services.business_classifier import classify_business_from_chatbot
from services.prompt_generator import generate_injection_prompts
from services.prompt_tester import test_single_prompt
from services.report_builder import build_security_report_pdf
import uuid
import asyncio

# Add vector db directory to Python path
vector_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'vector db')
sys.path.append(vector_db_path)

try:
    from vector_database import VectorDatabase
except ImportError as e:
    print(f"Error importing VectorDatabase: {e}")
    print(f"Looking for vector_database.py in: {vector_db_path}")
    raise

router = APIRouter()

@router.post("/audit", response_class=FileResponse)
async def audit_chatbot(request: SinglePromptRequest):
    chatbot_url = request.chatbot_url

    try:
        # Step 0: Initialize vector database
        db = VectorDatabase()

        # Step 1: Discover chatbot's business domain
        business_type = await classify_business_from_chatbot(chatbot_url)
        print(f"🏷️ Business Type: {business_type}")

        # Step 2: Generate injection prompts
        prompts = await generate_injection_prompts(business_type, count=5)
        print(f"🎭 Generated Prompts: {prompts}")

        # Step 3: Test each prompt and collect results
        tasks = [test_single_prompt(chatbot_url, p) for p in prompts]
        results = await asyncio.gather(*tasks)

        # Step 4: Store in vector DB
        for result in results:
            try:
                analysis_id = db.analyze_and_store(result.prompt, result.response)
                print(f"🧠 Stored in Vector DB with ID: {analysis_id}")
            except Exception as e:
                print(f"⚠️ Error storing in vector DB: {e}")

        # Step 5: Generate PDF Report
        file_name = f"reports/generated/audit_{uuid.uuid4().hex}.pdf"
        build_security_report_pdf(results, business_type, chatbot_url, file_name)

        # Step 6: Return PDF response
        return FileResponse(file_name, media_type='application/pdf', filename="audit_report.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"💥 Internal error: {str(e)}")

