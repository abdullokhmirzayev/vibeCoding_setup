---
name: pr-review
description: Use this skill to perform automated code reviews, check git diffs, ensure test coverage, and enforce coding standards.
---

# Pull Request Review Protocol

## Steps
1. Inspect git status and changed files:
   `git status --short`
2. Check recent diffs against main:
   `git diff main`
3. Execute the automated review audit script:
   `python3 ./scripts/run_audit.py`
4. Formulate actionable feedback:
   - Identify potential bugs or unhandled edge cases.
   - Verify unit test presence in `tests/`.
   - Validate compliance with [AGENTS.md](../../../AGENTS.md).
