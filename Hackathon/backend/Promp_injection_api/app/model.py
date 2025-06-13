from pydantic import BaseModel
from typing import List

class PromptInput(BaseModel):
    prompt: str

    def is_empty(self) -> bool:
        """Check if prompt string is empty or whitespace."""
        return not self.prompt.strip()

    def summary(self, max_length: int = 50) -> str:
        """Return a shortened version of the prompt for quick display."""
        return (self.prompt[:max_length] + '...') if len(self.prompt) > max_length else self.prompt

class InjectionFinding(BaseModel):
    test_name: str
    passed: bool
    reason: str

    def toggle_passed(self):
        """Toggle the passed status."""
        self.passed = not self.passed

    def __str__(self):
        status = "PASSED" if self.passed else "FAILED"
        return f"Test '{self.test_name}': {status} - {self.reason}"
    
    def __repr__(self):
        return f"InjectionFinding(test_name='{self.test_name}', passed={self.passed}, reason='{self.reason}')"
    
    def __eq__(self, other):
        if isinstance(other, InjectionFinding):
            return self.test_name == other.test_name and self.passed == other.passed and self.reason == other.reason
        return False

class PromptResult(BaseModel):
    prompt_id: str
    findings: List[InjectionFinding]

    def add_finding(self, finding: InjectionFinding):
        """Add a new injection finding to the list."""
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

