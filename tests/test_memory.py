import pytest
from src.memory.manager import memory_manager

def test_l2_rules_loaded():
    rules = memory_manager.get_l2_rules()
    assert len(rules) > 0
    assert "Safety First" in rules

def test_l4_memory_crud():
    test_content = "Always mock external payment gateways in tests"
    mem_id = memory_manager.add_l4_memory(test_content, category="testing")
    assert mem_id > 0

    results = memory_manager.query_l4_memory("payment gateways")
    assert len(results) > 0
    assert results[0]["content"] == test_content
