# manual_test.py
import asyncio
from services.business_classifier import classify_business

async def main():
    sample_input = "This assistant helps diagnose skin issues and recommends treatments."
    category = await classify_business(sample_input)
    print(f"🧠 Business Type: {category}")

asyncio.run(main())
