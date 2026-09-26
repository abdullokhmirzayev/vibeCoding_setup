import re
from typing import Dict, List, Tuple

# Common token and credential patterns
SECRET_PATTERNS: List[Tuple[str, str]] = [
    (r"sk-[a-zA-Z0-9]{20,}", "OPENAI_API_KEY"),
    (r"ghp_[a-zA-Z0-9]{36}", "GITHUB_PAT"),
    (r"gho_[a-zA-Z0-9]{36}", "GITHUB_OAUTH"),
    (r"AKIA[0-9A-Z]{16}", "AWS_ACCESS_KEY"),
    (r"-----BEGIN\s+(?:RSA|OPENSSH|EC)?\s*PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA|OPENSSH|EC)?\s*PRIVATE\s+KEY-----", "PRIVATE_KEY"),
    (r"ey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "JWT_TOKEN"),
    (r"(?:api_key|apikey|secret|password|access_token)\s*[:=]\s*[\"']([a-zA-Z0-9_\-\.]{8,})[\"']", "GENERIC_SECRET")
]

class SecretSanitizer:
    """
    Scans text payloads, logs, and tool outputs for sensitive tokens and credentials.
    Replaces matches with [REDACTED:<type>] to prevent data exfiltration.
    """
    @staticmethod
    def sanitize(text: str) -> Tuple[str, List[str]]:
        """
        Sanitizes text and returns (clean_text, list_of_redacted_types).
        """
        redacted_types = []
        clean_text = text

        for pattern, secret_type in SECRET_PATTERNS:
            matches = re.findall(pattern, clean_text, flags=re.IGNORECASE)
            if matches:
                redacted_types.append(secret_type)
                clean_text = re.sub(pattern, f"[REDACTED:{secret_type}]", clean_text, flags=re.IGNORECASE)

        return clean_text, redacted_types

    @staticmethod
    def contains_secrets(text: str) -> bool:
        """Checks if text contains any known secret pattern."""
        for pattern, _ in SECRET_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True
        return False

sanitizer = SecretSanitizer()
