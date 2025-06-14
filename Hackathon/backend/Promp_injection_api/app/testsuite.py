import uuid
from typing import List
from app.model import InjectionFinding

# Dictionary mapping test types to their severity levels and descriptions
KNOWN_ATTACKS = {
    "override_instructions": {
        "pattern": "ignore previous instructions",
        "severity": "HIGH",
        "description": "Attempt to override system instructions detected"
    },
    "system_role_injection": {
        "pattern": '{"role": "system"}',
        "severity": "CRITICAL",
        "description": "Attempt to inject system role detected"
    }
}

def run_tests(prompt: str) -> List[InjectionFinding]:
    findings = []
    for test_type, test_info in KNOWN_ATTACKS.items():
        location = {
            "start": prompt.lower().find(test_info["pattern"].lower()),
            "end": -1,
            "context": prompt
        }
        
        if location["start"] != -1:
            location["end"] = location["start"] + len(test_info["pattern"])
            findings.append(
                InjectionFinding(
                    type=test_type,
                    severity=test_info["severity"],
                    description=test_info["description"],
                    location=location
                )
            )

    return findings

def new_prompt_id() -> str:
    return uuid.uuid4().hex
