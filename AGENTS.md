# Project Agent Charter & Operating Guidelines

## Core Principles
1. **Safety First**: Never execute unverified destructive commands (`rm -rf`, `DROP TABLE`, `git push --force`). All actions are governed by deterministic hooks in `.agents/hooks.json`.
2. **Minimal Invasiveness**: Prefer minimal surgical edits over full-file rewrites. Preserve existing codebase structure and conventions.
3. **Progressive Disclosure**: Check `.agents/skills/` before attempting multi-step domain workflows (e.g. database migrations, security reviews).
4. **Verification**: Always execute unit tests and linting before marking any feature complete.
5. **No Secret Leaks**: Never print, commit, or log credentials, tokens, or `.env` files.
