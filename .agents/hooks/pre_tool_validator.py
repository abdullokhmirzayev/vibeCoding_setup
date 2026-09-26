#!/usr/bin/env python3
"""
PreToolUse Hook: Deterministic Safety Gate
Receives: JSON payload on stdin
Returns: JSON response on stdout {"decision": "allow" | "deny" | "ask"}
"""
import sys
import json
import re

DENY_PATTERNS = [
    r"rm\s+-rf\s+/",
    r":\(\)\{\s*:\|:&\s*\};:",  # Fork bomb
    r"mkfs",
    r"dd\s+if=",
    r"git\s+push\s+.*--force",
    r"DROP\s+DATABASE",
]

APPROVAL_REQUIRED_PATTERNS = [
    r"kubectl\s+delete",
    r"terraform\s+apply",
    r"npm\s+publish",
    r"git\s+reset\s+--hard",
]

def evaluate():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({"decision": "allow"}))
            return
        data = json.loads(raw)
    except Exception as e:
        print(json.dumps({"decision": "deny", "reason": f"Invalid JSON payload: {e}"}))
        return

    tool_call = data.get("toolCall", {})
    args = tool_call.get("args", {})
    cmd = args.get("CommandLine", "")

    # 1. Hard Block (Zero Trust)
    for pattern in DENY_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            print(json.dumps({
                "decision": "deny",
                "reason": f"SECURITY POLICY VIOLATION: Disallowed destructive pattern detected -> '{pattern}'"
            }))
            return

    # 2. Human-in-the-Loop Escalation
    for pattern in APPROVAL_REQUIRED_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            print(json.dumps({
                "decision": "ask",
                "reason": f"HIGH IMPACT ACTION: Command matches '{pattern}'. Operator confirmation required."
            }))
            return

    # 3. Allow execution
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    evaluate()
