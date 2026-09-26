import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["governance"] == "active"

def test_governance_check_deny():
    resp = client.post("/api/v1/governance/check", json={"command": "rm -rf /"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "deny"
    assert "destructive" in data["reason"].lower()

def test_governance_check_allow():
    resp = client.post("/api/v1/governance/check", json={"command": "git status"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "allow"

def test_skills_list_and_detail():
    resp = client.get("/api/v1/skills")
    assert resp.status_code == 200
    skills = resp.json()
    assert len(skills) >= 4  # database-migration, pr-review, security-audit, docker-deploy

    skill_names = [s["name"] for s in skills]
    assert "pr-review" in skill_names
    assert "security-audit" in skill_names

    # Check detail endpoint
    detail_resp = client.get("/api/v1/skills/pr-review")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert "run_audit.py" in detail["scripts"]

def test_memory_api():
    create_resp = client.post("/api/v1/memory", json={
        "content": "API test preference: always use strict typing",
        "category": "api_test"
    })
    assert create_resp.status_code == 200
    assert create_resp.json()["status"] == "created"

    list_resp = client.get("/api/v1/memory?query=strict typing")
    assert list_resp.status_code == 200
    memories = list_resp.json()
    assert len(memories) > 0
    assert "strict typing" in memories[0]["content"]

def test_agent_run():
    resp = client.post("/api/v1/agent/run", json={
        "query": "Inspect current repository setup",
        "execute_safe_commands": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "llm_response" in data
    assert "model_used" in data
