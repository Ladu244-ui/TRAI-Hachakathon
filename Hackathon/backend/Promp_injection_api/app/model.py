from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class InjectionFinding(BaseModel):
    type: str = Field(..., description="Type of injection vulnerability found")
    severity: str = Field(..., description="Severity level of the finding")
    description: str = Field(..., description="Detailed description of the finding")
    location: Dict[str, Any] = Field(..., description="Location information of the finding")
    passed: bool = Field(..., description="Whether the test passed or failed")

class PromptInput(BaseModel):
    prompt: str = Field(..., min_length=1, description="The prompt to be tested")
    context: Optional[str] = Field(None, description="Additional context for the prompt")

class PromptResult(BaseModel):
    prompt_id: str
    findings: List[InjectionFinding] = Field(default_factory=list)

    def add_finding(self, finding: InjectionFinding):
        """Add a new finding to the results list."""
        self.findings.append(finding)

    def passed_count(self) -> int:
        """Return the number of tests that passed (no injection vulnerability found)."""
        return sum(f.passed for f in self.findings)

    def failed_count(self) -> int:
        """Return the number of tests that failed (vulnerability found)."""
        return sum(not f.passed for f in self.findings)

    def summary(self) -> str:
        """Provide a summary of how many tests passed or failed."""
        total = len(self.findings)
        passed = self.passed_count()
        failed = self.failed_count()
        return f"Prompt {self.prompt_id}: {passed}/{total} passed, {failed} failed."
