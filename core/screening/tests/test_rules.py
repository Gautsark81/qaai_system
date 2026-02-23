from core.screening.rules import evaluate_rules
from core.screening.rule_types import RuleCategory


def test_rules_return_structured_metadata():
    rules = evaluate_rules("RELIANCE")

    assert isinstance(rules, dict)
    assert len(rules) > 0

    for name, meta in rules.items():
        assert "passed" in meta
        assert "weight" in meta
        assert "category" in meta
        assert isinstance(meta["passed"], bool)
        assert meta["weight"] > 0
        assert isinstance(meta["category"], RuleCategory)
