import re
import json
from typing import Dict, Tuple

class PromptNormalizer:
    def __init__(self):
        # Common patterns for PII and non-deterministic information
        self.patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            'timestamp': r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?',
            'date': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            'username': r'@[\w\d_]+',
            'url': r'https?://\S+',
            'ip': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        }

    def _remove_pii(self, text: str) -> str:
        """Remove personally identifiable information from text"""
        # Replace each pattern with a placeholder
        normalized = text
        for pattern_name, pattern in self.patterns.items():
            normalized = re.sub(pattern, f'[{pattern_name.upper()}]', normalized)
        return normalized

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        # Replace multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        normalized = normalized.strip()
        return normalized

    def _remove_special_chars(self, text: str) -> str:
        """Remove or normalize special characters"""
        # Replace special characters with space
        normalized = re.sub(r'[^\w\s.,!?-]', ' ', text)
        return self._normalize_whitespace(normalized)

    def normalize(self, prompt: str, response: str) -> Dict[str, str]:
        """Normalize a prompt-response pair and return as JSON"""
        # Clean prompt and response
        normalized_prompt = self._remove_pii(prompt)
        normalized_prompt = self._remove_special_chars(normalized_prompt)

        normalized_response = self._remove_pii(response)
        normalized_response = self._remove_special_chars(normalized_response)

        # Create JSON structure
        normalized_data = {
            "prompt": normalized_prompt,
            "response": normalized_response
        }

        return normalized_data

# Example usage
if __name__ == "__main__":
    normalizer = PromptNormalizer()
    
    # Example prompt-response pair with PII
    prompt = "Hi @john_doe, my email is user@example.com. What's the weather like on 2023-10-15?"
    response = "Hello! The weather on 10/15/2023 at 14:30:00 GMT will be sunny. Contact support at https://weather.com/support."
    
    # Normalize the data
    normalized = normalizer.normalize(prompt, response)
    print(json.dumps(normalized, indent=2))