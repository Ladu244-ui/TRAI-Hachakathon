from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from schemas.schemas import SinglePromptRequest
from services.business_classifier import classify_business_from_chatbot
from services.prompt_generator import generate_injection_prompts
from services.prompt_tester import test_single_prompt
from services.report_builder import build_security_report_pdf
import uuid
import asyncio

router = APIRouter()

@router.post("/audit", response_class=FileResponse)
async def audit_chatbot(request: SinglePromptRequest):
    chatbot_url = request.chatbot_url

    try:
        # Step 1: Discover chatbot's business domain
        business_type = await classify_business_from_chatbot(chatbot_url)
        print(f"🏷️ Business Type: {business_type}")

        # Step 2: Generate injection prompts
        prompts = await generate_injection_prompts(business_type, count=5)
        print(f"🎭 Generated Prompts: {prompts}")

        # Step 3: Test each prompt and collect results
        tasks = [test_single_prompt(chatbot_url, p) for p in prompts]
        results = await asyncio.gather(*tasks)

        # Step 4: Generate PDF Report
        file_name = f"reports/generated/audit_{uuid.uuid4().hex}.pdf"
        print(file_name)
        build_security_report_pdf(results, business_type, chatbot_url, file_name)

        # Step 5: Return PDF response
        return FileResponse(file_name, media_type='application/pdf', filename="audit_report.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"💥 Internal error: {str(e)}")
