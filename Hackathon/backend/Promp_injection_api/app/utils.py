import uuid
from typing import Dict, Any, List
from .model import InjectionFinding

def new_prompt_id() -> str:
    """Generate a unique identifier for a prompt test.
    
    Returns:
        str: A unique UUID string
    """
    return str(uuid.uuid4())

def check_injection_patterns(prompt: str) -> List[Dict[str, Any]]:
    """Check for common injection patterns in the prompt.
    
    Args:
        prompt (str): The prompt text to analyze
        
    Returns:
        List[Dict[str, Any]]: List of detected injection patterns
    """
    patterns = [
        {"pattern": "system.run", "type": "Command Injection", "severity": "high"},
        {"pattern": "exec(", "type": "Code Execution", "severity": "high"},
        {"pattern": "import os", "type": "System Access", "severity": "high"},
        {"pattern": "http://", "type": "URL Injection", "severity": "medium"},
        {"pattern": "https://", "type": "URL Injection", "severity": "medium"}
    ]
    
    findings = []
    for pattern in patterns:
        if pattern["pattern"] in prompt.lower():
            findings.append({
                "type": pattern["type"],
                "severity": pattern["severity"],
                "description": f"Found potential {pattern['type']} pattern",
                "location": {"pattern": pattern["pattern"]}
            })
    return findings

def analyze_prompt_structure(prompt: str) -> List[Dict[str, Any]]:
    """Analyze the structure of the prompt for potential vulnerabilities.
    
    Args:
        prompt (str): The prompt text to analyze
        
    Returns:
        List[Dict[str, Any]]: List of structural findings
    """
    findings = []
    
    # Check prompt length
    if len(prompt) > 1000:
        findings.append({
            "type": "Length Warning",
            "severity": "low",
            "description": "Prompt exceeds recommended length",
            "location": {"length": len(prompt)}
        })
    
    # Check for multiple commands
    if prompt.count(';') > 2:
        findings.append({
            "type": "Multiple Commands",
            "severity": "medium",
            "description": "Multiple command sequences detected",
            "location": {"separator_count": prompt.count(';')}
        })
    
    return findings

def run_tests(prompt: str) -> Dict[str, Any]:
    """Run all security tests on the provided prompt.
    
    Args:
        prompt (str): The prompt to test
        
    Returns:
        Dict[str, Any]: Combined test results and findings
    """
    findings = []
    
    # Run injection pattern checks
    injection_findings = check_injection_patterns(prompt)
    findings.extend(injection_findings)
    
    # Run structural analysis
    structure_findings = analyze_prompt_structure(prompt)
    findings.extend(structure_findings)
    
    # Calculate overall risk score
    risk_score = calculate_risk_score(findings)
    
    return {
        "findings": findings,
        "risk_score": risk_score,
        "total_findings": len(findings)
    }

def calculate_risk_score(findings: List[Dict[str, Any]]) -> float:
    """Calculate the overall risk score based on findings.
    
    Args:
        findings (List[Dict[str, Any]]): List of security findings
        
    Returns:
        float: Risk score between 0 and 1
    """
    if not findings:
        return 0.0
    
    severity_weights = {
        "high": 1.0,
        "medium": 0.5,
        "low": 0.2
    }
    
    total_weight = sum(severity_weights[f["severity"]] for f in findings)
    max_weight = len(findings)
    
    return min(1.0, total_weight / max_weight if max_weight > 0 else 0.0)

# In-memory storage for results (replace with database in production)
_results_store: Dict[str, Dict[str, Any]] = {}

def save_result(prompt_id: str, data: Dict[str, Any]) -> bool:
    """Save test results to storage.
    
    Args:
        prompt_id (str): Unique identifier for the test
        data (Dict[str, Any]): Test results data
        
    Returns:
        bool: True if save was successful
    """
    _results_store[prompt_id] = data
    return True

def fetch_result(prompt_id: str) -> Dict[str, Any] | None:
    """Retrieve test results from storage.
    
    Args:
        prompt_id (str): Unique identifier for the test
        
    Returns:
        Dict[str, Any] | None: Test results or None if not found
    """
    return _results_store.get(prompt_id)