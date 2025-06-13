# tests/test_business_classifier.py
import pytest
import asyncio
from services.business_classifier import classify_business

@pytest.mark.asyncio
async def test_healthcare_classification():
    input_text = "This chatbot reminds patients to take their medication and logs their symptoms."
    result = await classify_business(input_text)
    assert "healthcare" in result

@pytest.mark.asyncio
async def test_ecommerce_classification():
    input_text = "We run an online store that uses a recommender chatbot to boost sales."
    result = await classify_business(input_text)
    assert "ecommerce" in result

@pytest.mark.asyncio
async def test_education_classification():
    input_text = "Our math tutor chatbot helps learners practice algebra and geometry."
    result = await classify_business(input_text)
    assert "education" in result
