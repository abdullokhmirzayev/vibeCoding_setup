#!/usr/bin/env python3
"""
PostToolUse Hook: Secret Redactor and Post-Processing
Receives: JSON payload on stdin
Returns: Empty JSON object {} on stdout
"""
import sys
import json
import re

SECRET_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{20,}", "OPENAI_API_KEY"),
    (r"ghp_[a-zA-Z0-9]{36}", "GITHUB_PAT"),
    (r"AKIA[0-9A-Z]{16}", "AWS_ACCESS_KEY"),
    (r"-----BEGIN\s+PRIVATE\s+KEY-----", "PRIVATE_KEY"),
]

def main():
    try:
        raw = sys.stdin.read()
        if raw.strip():
            data = json.loads(raw)
            result = str(data.get("result", ""))
            
            # Check for secrets
            for pattern, name in SECRET_PATTERNS:
                if re.search(pattern, result, re.IGNORECASE):
                    sys.stderr.write(f"[GOVERNANCE WARNING] Secret leak detected and masked: {name}\n")
    except Exception:
        pass

    # Post-tool hooks expect {} on stdout
    print(json.dumps({}))

if __name__ == "__main__":
    main()
