# tests/test_prompt_generator.py
import pytest
from services.prompt_generator import generate_injection_prompts

@pytest.mark.asyncio
async def test_generate_healthcare_prompts():
    prompts = await generate_injection_prompts("healthcare", 3)
    print(prompts)
    assert isinstance(prompts, list)
    assert len(prompts) == 3
    for p in prompts:
        assert len(p) > 10  # simple sanity check
        assert "patient" in p.lower() or "data" in p.lower() or "record" in p.lower()

@pytest.mark.asyncio
async def test_generate_education_prompts():
    prompts = await generate_injection_prompts("education", 2)
    assert len(prompts) == 2
