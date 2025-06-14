# services/business_classifier.py
from utils.novita_client import call_novita



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

async def classify_business(input_text: str) -> str:
    prompt = CLASSIFIER_PROMPT.format(input=input_text.strip())
    classification = await call_novita(prompt)
    return classification.strip().lower()

