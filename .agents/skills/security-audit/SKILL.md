---
name: security-audit
description: Use this skill to run static security audits, detect hardcoded secrets, and scan files for high-risk dependencies.
---

# Security Audit Protocol

## Steps
1. Scan project for accidental secret leaks using the scanner script:
   `python3 ./scripts/scan_secrets.py`
2. Check `.gitignore` to ensure `.env*`, `.pem`, and credential files are excluded.
3. Verify that all external HTTP requests are routed through verified endpoints.
4. Report any findings with severity rankings (Low, Medium, High, Critical).
