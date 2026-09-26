import pytest
from src.skills.registry import skill_registry

def test_skill_discovery():
    skills = skill_registry.list_available_skills()
    assert len(skills) > 0

    names = [s.name for s in skills]
    assert "database-migration" in names

def test_progressive_disclosure():
    # Verify metadata is lightweight
    skill = [s for s in skill_registry.list_available_skills() if s.name == "database-migration"][0]
    assert skill.description != ""
    assert skill.has_scripts is True

    # Verify detail is loaded on-demand
    detail = skill_registry.get_skill_detail("database-migration")
    assert detail is not None
    assert "Runbook" in detail.content
    assert len(detail.scripts) > 0
