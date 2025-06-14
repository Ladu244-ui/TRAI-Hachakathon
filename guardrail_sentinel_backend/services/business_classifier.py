# services/business_classifier.py
from utils.novita_client import call_novita
from schemas.prompt_test import PromptTestResult
import requests



CLASSIFIER_PROMPT = """
Classify the business type from this description or content. Respond with a one-word business category only.

Examples:
- "We help patients manage chronic illness via chatbot." -> healthcare
- "We sell clothes online with personalized recommendations." -> ecommerce
- "We tutor students using a math chatbot." -> education

Input:
{input}
Respond with a one-word business category only.
"""

CHATBOT_DISCOVERY_PROMPT = "Can you briefly describe the purpose of this chatbot or the business you're supporting?"

async def classify_business(input_text: str) -> str:
    prompt = CLASSIFIER_PROMPT.format(input=input_text.strip())
    classification = await call_novita(prompt)
    return classification.strip().lower()

async def classify_business_from_chatbot(chatbot_url: str) -> str:
    """
    Step 1: Ask the chatbot about its purpose.
    Step 2: Use that response to classify the business.
    """

    try:
        print("🔎 Interrogating chatbot for business context...")
        res = requests.post(chatbot_url, json={"prompt": CHATBOT_DISCOVERY_PROMPT}, timeout=10)
        res.raise_for_status()
        data = res.json()

        chatbot_description = ""
        for key in ['ciphergenix_response', 'response', 'message', 'reply', 'text']:
            if key in data:
                chatbot_description = data[key]
                break

        if not chatbot_description:
            chatbot_description = str(data)

        print(f"💬 Chatbot described itself as: {chatbot_description}")

        return await classify_business(chatbot_description)

    except Exception as e:
        print(f"❌ Failed to classify from chatbot: {e}")
        return "unknown"