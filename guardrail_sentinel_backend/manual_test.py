# manual_test.py
import asyncio
from services.business_classifier import classify_business
from services.prompt_generator import generate_injection_prompts
from services.prompt_tester import test_single_prompt

# async def main():
#     sample_input = "This assistant helps diagnose skin issues and recommends treatments."
#     category = await classify_business(sample_input)
#     print(f"🧠 Business Type: {category}")


# async def main():
#     prompts = await generate_injection_prompts("ecommerce", 4)
#     print("🧨 Injection Prompts:")
#     for i, p in enumerate(prompts, 1):
#         print(f"{i}. {p}")


async def main():
    business_type = "Commertial LLM"
    endpoint = "https://api.us-south.assistant.watson.cloud.ibm.com"
    
    prompts = await generate_injection_prompts(business_type, 3)
    results = []

    for p in prompts:
        result = await test_single_prompt(endpoint, p)
        results.append(result)

    print("🧪 Prompt Test Results:")
    for r in results:
        print(f"\nPrompt: {r.prompt}\nResponse: {r.response}\nSuccess: {r.is_success}\nNotes: {r.notes}\n")

asyncio.run(main())
