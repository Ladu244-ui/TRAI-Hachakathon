import uuid
from typing import Dict, Any, List
from app.model import InjectionFinding

def new_prompt_id() -> str:
    return str(uuid.uuid4())

def check_injection_patterns(prompt: str) -> List[InjectionFinding]:
    patterns = [
        {"pattern": "system.run", "type": "Command Injection", "severity": "high"},
        {"pattern": "exec(", "type": "Code Execution", "severity": "high"},
        {"pattern": "import os", "type": "System Access", "severity": "high"},
        {"pattern": "http://", "type": "URL Injection", "severity": "medium"},
        {"pattern": "https://", "type": "URL Injection", "severity": "medium"},
        {"pattern": "eval(", "type": "Code Execution", "severity": "high"},
        {"pattern": "subprocess", "type": "System Access", "severity": "high"},
        {"pattern": "file:", "type": "File Access", "severity": "high"}
    ]
    
    findings = []
    for pattern in patterns:
        if pattern["pattern"] in prompt.lower():
            findings.append(InjectionFinding(
                type=pattern["type"],
                severity=pattern["severity"],
                description=f"Found potential {pattern['type']} pattern",
                location={"pattern": pattern["pattern"], "index": prompt.lower().index(pattern["pattern"])}
            ))
    return findings

def analyze_prompt_structure(prompt: str) -> List[InjectionFinding]:
    findings = []
    
    # Check prompt length
    if len(prompt) > 1000:
        findings.append(InjectionFinding(
            type="Length Warning",
            severity="low",
            description="Prompt exceeds recommended length of 1000 characters",
            location={"length": len(prompt), "limit": 1000}
        ))
    
    # Check for multiple commands
    command_count = prompt.count(';')
    if command_count > 2:
        findings.append(InjectionFinding(
            type="Multiple Commands",
            severity="medium",
            description=f"Found {command_count} command sequences (limit: 2)",
            location={"separator_count": command_count, "limit": 2}
        ))
    
    # Check for suspicious characters
    suspicious_chars = {'$', '`', '|', '&', '>'}
    found_chars = {char for char in suspicious_chars if char in prompt}
    if found_chars:
        findings.append(InjectionFinding(
            type="Suspicious Characters",
            severity="medium",
            description=f"Found suspicious characters: {', '.join(found_chars)}",
            location={"characters": list(found_chars)}
        ))
    
    return findings

def run_tests(prompt: str) -> Dict[str, Any]:
    findings = []
    
    # Run all security checks
    findings.extend(check_injection_patterns(prompt))
    findings.extend(analyze_prompt_structure(prompt))
    
    # Convert findings to dict format for storage
    findings_dict = [f.dict() for f in findings]
    
    # Calculate risk score
    risk_score = calculate_risk_score(findings_dict)
    
    return {
        "findings": findings_dict,
        "risk_score": risk_score,
        "total_findings": len(findings)
    }

def calculate_risk_score(findings: List[Dict[str, Any]]) -> float:
    if not findings:
        return 0.0
    
    severity_weights = {
        "high": 1.0,
        "medium": 0.5,
        "low": 0.2
    }
    
    total_weight = sum(severity_weights[f["severity"]] for f in findings)
    max_possible_weight = len(findings)  # Maximum possible weight if all findings were high severity
    
    # Normalize score between 0 and 1
    return min(1.0, total_weight / max_possible_weight if max_possible_weight > 0 else 0.0)

# In-memory storage
_results_store: Dict[str, Dict[str, Any]] = {}

def save_result(prompt_id: str, data: Dict[str, Any]) -> bool:
    try:
        _results_store[prompt_id] = data
        return True
    except Exception:
        return False

def fetch_result(prompt_id: str) -> Dict[str, Any] | None:
    return _results_store.get(prompt_id)