from typing import List, Dict, Set
from dataclasses import dataclass
import re
from vulnerability_classifier import VulnerabilityClassifier

@dataclass
class TagCategory:
    name: str
    patterns: Dict[str, List[str]]
    prefix: str

class TagGenerator:
    def __init__(self):
        self.vulnerability_classifier = VulnerabilityClassifier()
        
        # Define tag categories and their patterns
        self.categories = [
            TagCategory(
                name="intent",
                patterns={
                    "question": [r"\?$", r"^(what|how|why|when|where|who)"],
                    "command": [r"^(please|can you|could you)", r"^(show|tell|give|explain)"],
                    "statement": [r"^[A-Z][^?!.]*\.$"],
                    "request": [r"I (need|want|would like)", r"(help|assist)"],
                },
                prefix="intent"
            ),
            TagCategory(
                name="response_type",
                patterns={
                    "denial": [r"(cannot|can't|won't|will not|unable)", r"not (allowed|permitted)"],
                    "explanation": [r"because", r"(as|since|due to)"],
                    "alternative": [r"(instead|however|alternatively)", r"you (can|could|may)"],
                    "warning": [r"(warning|caution|alert)", r"(dangerous|unsafe|risky)"],
                },
                prefix="response"
            ),
            TagCategory(
                name="content_type",
                patterns={
                    "code": [r"```", r"\bcode\b", r"function", r"class", r"var"],
                    "data": [r"\b(json|xml|csv)\b", r"database", r"schema"],
                    "security": [r"password", r"token", r"key", r"access", r"permission"],
                    "system": [r"\b(os|system|kernel|root)\b", r"\b(cpu|memory|disk)\b"],
                },
                prefix="content"
            )
        ]

    def _extract_category_tags(self, text: str, category: TagCategory) -> Set[str]:
        """Extract tags for a specific category based on patterns"""
        tags = set()
        for tag_name, patterns in category.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    tags.add(f"{category.prefix}:{tag_name}")
                    break
        return tags

    def _extract_language_tags(self, text: str) -> Set[str]:
        """Extract programming language tags"""
        language_patterns = {
            "python": r"\b(python|pip|django|flask)\b",
            "javascript": r"\b(javascript|node|npm|react|vue)\b",
            "java": r"\b(java|spring|maven|gradle)\b",
            "sql": r"\b(sql|mysql|postgresql|oracle)\b"
        }
        
        tags = set()
        for lang, pattern in language_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                tags.add(f"lang:{lang}")
        return tags

    def generate_tags(self, prompt: str, response: str) -> Dict[str, object]:
        """Generate metadata tags for a prompt-response pair"""
        all_tags = set()
        combined_text = f"{prompt}\n{response}"
        
        # Get vulnerability classification
        vuln_result = self.vulnerability_classifier.classify(prompt, response)
        if vuln_result["type"] != "none":
            all_tags.add(f"vulnerability:{vuln_result['type']}")
            all_tags.add(f"risk:{'high' if vuln_result['confidence'] > 0.7 else 'medium' if vuln_result['confidence'] > 0.4 else 'low'}")
        
        # Extract category-based tags
        for category in self.categories:
            # Get tags from both prompt and response
            prompt_tags = self._extract_category_tags(prompt, category)
            response_tags = self._extract_category_tags(response, category)
            all_tags.update(prompt_tags)
            all_tags.update(response_tags)
        
        # Extract language-specific tags
        language_tags = self._extract_language_tags(combined_text)
        all_tags.update(language_tags)
        
        # Add complexity tag based on text length and structure
        total_length = len(prompt) + len(response)
        if total_length > 500 or len(prompt.split()) > 50:
            all_tags.add("complexity:high")
        elif total_length > 200 or len(prompt.split()) > 20:
            all_tags.add("complexity:medium")
        else:
            all_tags.add("complexity:low")
        
        # Format output
        return {
            "tags": sorted(list(all_tags)),
            "metadata": {
                "prompt_length": len(prompt),
                "response_length": len(response),
                "vulnerability_type": vuln_result["type"],
                "vulnerability_confidence": vuln_result["confidence"]
            }
        }

# Example usage
if __name__ == "__main__":
    generator = TagGenerator()
    
    # Example prompt-response pair
    prompt = "Can you help me write a Python function to access system files?"
    response = "I cannot provide code that might compromise system security. Instead, I can show you safe file handling practices."
    
    # Generate tags
    result = generator.generate_tags(prompt, response)
    
    # Print results
    print("Generated Tags:")
    for tag in result["tags"]:
        print(f"- {tag}")
    print("\nMetadata:")
    for key, value in result["metadata"].items():
        print(f"{key}: {value}")