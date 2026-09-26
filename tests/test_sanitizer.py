import pytest
from src.governance.sanitizer import sanitizer

def test_sanitize_openai_key():
    dirty = "My secret key is sk-abcdef1234567890abcdef123456"
    clean, types = sanitizer.sanitize(dirty)
    assert "[REDACTED:OPENAI_API_KEY]" in clean
    assert "sk-" not in clean
    assert "OPENAI_API_KEY" in types

def test_sanitize_github_pat():
    dirty = "curl -H 'Authorization: token ghp_123456789012345678901234567890123456'"
    clean, types = sanitizer.sanitize(dirty)
    assert "[REDACTED:GITHUB_PAT]" in clean
    assert "ghp_" not in clean
    assert "GITHUB_PAT" in types

def test_contains_secrets():
    assert sanitizer.contains_secrets("AKIAIOSFODNN7EXAMPLE") is True
    assert sanitizer.contains_secrets("Hello world, clean text!") is False
