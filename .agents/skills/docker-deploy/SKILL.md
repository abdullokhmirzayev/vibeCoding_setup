---
name: docker-deploy
description: Use this skill to validate docker compose infrastructure, check container health, and manage deployment lifecycle.
---

# Docker Deployment Runbook

## Protocol
1. Validate docker compose configuration:
   `docker compose config --quiet`
2. Run automated infrastructure health verification:
   `python3 ./scripts/health_check.py`
3. Launch services in detached mode:
   `docker compose up -d`
4. Inspect running container states:
   `docker compose ps`
