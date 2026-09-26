import re
from typing import Tuple

DENY_COMMAND_PATTERNS = [
    (r"rm\s+-rf\s+/", "Disallowed destructive root filesystem deletion"),
    (r":\(\)\{\s*:\|:&\s*\};:", "Fork bomb detected"),
    (r"mkfs", "Filesystem formatting disallowed"),
    (r"dd\s+if=", "Raw disk write disallowed"),
    (r"git\s+push\s+.*--force", "Force push to git branches disallowed"),
    (r"DROP\s+DATABASE", "Raw drop database disallowed"),
]

ASK_COMMAND_PATTERNS = [
    (r"kubectl\s+delete", "Cluster resource deletion requires operator approval"),
    (r"terraform\s+apply", "Infrastructure mutation requires operator approval"),
    (r"npm\s+publish", "Package publishing requires operator approval"),
    (r"git\s+reset\s+--hard", "Git history rewrite requires operator approval"),
]

def check_command_safety(command: str) -> Tuple[str, str]:
    """
    Evaluates command against zero-trust policy.
    Returns: (decision: 'allow' | 'deny' | 'ask', reason: str)
    """
    for pattern, reason in DENY_COMMAND_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "deny", f"SECURITY POLICY VIOLATION: {reason} (pattern: {pattern})"

    for pattern, reason in ASK_COMMAND_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "ask", f"HIGH IMPACT ACTION: {reason} (pattern: {pattern})"

    return "allow", "Command passed static governance checks"
