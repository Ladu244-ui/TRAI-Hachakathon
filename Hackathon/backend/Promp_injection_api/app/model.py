from pydantic import BaseModel, Field
from typing import List, Dict, Any

class InjectionFinding(BaseModel):
    type: str = Field(..., description="Type of injection vulnerability found")
    severity: str = Field(..., description="Severity level of the finding")
    description: str = Field(..., description="Detailed description of the finding")
    location: Dict[str, Any] = Field(..., description="Location information of the finding")

class PromptInput(BaseModel):
    prompt: str = Field(..., min_length=1, description="The prompt to be tested")
    context: str | None = Field(None, description="Additional context for the prompt")

class PromptResult(BaseModel):
    prompt_id: str
    findings: List[InjectionFinding] = Field(default_factory=list)

    def add_finding(self, finding: InjectionFinding):
        self.findings.append(finding)

    def passed_count(self) -> int:
        """Return number of tests passed."""
        return sum(f.passed for f in self.findings)

    def failed_count(self) -> int:
        """Return number of tests failed."""
        return sum(not f.passed for f in self.findings)

    def summary(self) -> str:
        """Provide a summary string of the results."""
        total = len(self.findings)
        passed = self.passed_count()
        failed = self.failed_count()
        return f"Prompt {self.prompt_id}: {passed}/{total} passed, {failed} failed."

