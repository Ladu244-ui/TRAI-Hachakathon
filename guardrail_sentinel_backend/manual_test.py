# manual_test.py
import asyncio
import requests
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
    endpoint = "https://web-production-8e40c.up.railway.app/chat/"
    
    prompts = await generate_injection_prompts(business_type, 3)
    results = []

    for p in prompts:
        result = await test_single_prompt(endpoint, p)
        results.append(result)
    # print(results)

    print("🧪 Prompt Test Results:")
    for r in results:
        print(f"\nPrompt: {r.prompt}\nResponse: {r.response}\nSuccess: {r.is_success}\nNotes: {r.notes}\n")


asyncio.run(main())


# def send_prompt_to_chatbot(prompt: str, chatbot_url: str) -> str:
#     if not prompt.strip():
#         return "⚠️ Prompt cannot be empty."

#     try:
#         response = requests.post(chatbot_url, json={"prompt": prompt}, timeout=10)
#         response.raise_for_status()  # Raises HTTPError for bad responses (4xx/5xx)

#         # Try extracting chatbot response safely
#         data = response.json()

#         print(data)

#         # Attempt common response keys — can be customized per chatbot
#         for key in ['ciphergenix_response', 'response', 'message', 'reply', 'text']:
#             if key in data:
#                 return f"🤖 {data[key]}"

#         # If unknown format, return raw data
#         return f"📦 Raw response: {data}"

#     except requests.exceptions.RequestException as e:
#         return f"❌ Network error or timeout: {str(e)}"
#     except ValueError:
#         return "🚨 Response is not valid JSON."
#     except Exception as e:
#         return f"💥 Unexpected error: {str(e)}"

# prompt = "What's the weather like on Mars?"
# chatbot_url = "https://web-production-8e40c.up.railway.app/chat/"  # or any other chatbot

# result = send_prompt_to_chatbot(prompt, chatbot_url)
# print(result)
