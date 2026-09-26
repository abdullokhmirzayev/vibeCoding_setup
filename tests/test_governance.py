import pytest
from src.governance.hook_engine import hook_engine
from src.governance.policies import check_command_safety

def test_static_policy_deny():
    decision, reason = check_command_safety("rm -rf /")
    assert decision == "deny"
    assert "destructive" in reason.lower()

    decision, reason = check_command_safety("git push origin main --force")
    assert decision == "deny"

    decision, reason = check_command_safety("DROP DATABASE production")
    assert decision == "deny"

def test_static_policy_ask():
    decision, reason = check_command_safety("kubectl delete pod my-pod")
    assert decision == "ask"

    decision, reason = check_command_safety("git reset --hard HEAD~1")
    assert decision == "ask"

def test_static_policy_allow():
    decision, reason = check_command_safety("git status")
    assert decision == "allow"

    decision, reason = check_command_safety("npm test")
    assert decision == "allow"

def test_hook_engine_pre_tool_call():
    # Test through the actual HookEngine calling python pre_tool_validator.py
    decision = hook_engine.run_pre_tool_hook("run_command", {"CommandLine": "rm -rf /"})
    assert decision.decision == "deny"

    decision = hook_engine.run_pre_tool_hook("run_command", {"CommandLine": "git reset --hard"})
    assert decision.decision == "ask"

    decision = hook_engine.run_pre_tool_hook("run_command", {"CommandLine": "ls -la"})
    assert decision.decision == "allow"
