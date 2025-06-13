import uuid
from typing import List
from .models import InjectionFinding

# 🚩  Very naive tests for now; we’ll expand later
KNOWN_ATTACKS = [
    ("override_instructions", "ignore previous instructions"),
    ("system_role_injection", '{"role": "system"}'),
]

def run_tests(prompt: str) -> List[InjectionFinding]:
    findings = []
    for name, needle in KNOWN_ATTACKS:
        if needle.lower() in prompt.lower():
            findings.append(
                InjectionFinding(
                    test_name=name,
                    passed=False,
                    reason=f"Matched pattern: {needle}"
                )
            )
        else:
            findings.append(
                InjectionFinding(
                    test_name=name,
                    passed=True,
                    reason="No match"
                )
            )
    return findings

def new_prompt_id() -> str:
    return uuid.uuid4().hex
