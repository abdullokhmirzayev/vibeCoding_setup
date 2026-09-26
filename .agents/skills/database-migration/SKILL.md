---
name: database-migration
description: Use this skill whenever generating, testing, or applying relational database schema changes.
---

# Database Migration Runbook

## Safety Prerequisites
1. Ensure a local database dump exists before running migrations.
2. Dry-run the migration schema:
   `python3 ./scripts/run_dry_run.py`

## Execution Protocol
1. Verify column nullability constraints.
2. If adding an index on a table > 100k rows, use `CONCURRENTLY`.
3. Check the execution logs before concluding.
