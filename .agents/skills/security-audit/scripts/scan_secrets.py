#!/usr/bin/env python3
"""
Static Secret Scanner Script
"""
import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from src.governance.sanitizer import sanitizer

def main():
    violations = 0

    print("[SECURITY-SCAN] Scanning repository for leaked credentials...")
    for ext in ["*.py", "*.json", "*.yml", "*.yaml", "*.md"]:
        for file in root.rglob(ext):
            if ".git" in file.parts or ".venv" in file.parts or "node_modules" in file.parts:
                continue
            try:
                content = file.read_text(encoding="utf-8", errors="ignore")
                _, found = sanitizer.sanitize(content)
                # Filter out intentional detector definitions
                real_leaks = [f for f in found if "sanitizer.py" not in file.name and "post_tool_sanitizer.py" not in file.name]
                if real_leaks:
                    print(f"❌ [SECRET DETECTED] {file.relative_to(root)}: {real_leaks}")
                    violations += 1
            except Exception:
                pass

    if violations > 0:
        print(f"\n[SECURITY-SCAN] Scan failed with {violations} violation(s).")
        sys.exit(1)
    else:
        print("[SECURITY-SCAN] Zero hardcoded secrets detected. Clean!")
        sys.exit(0)

if __name__ == "__main__":
    main()
