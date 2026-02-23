import inspect

from core.strategy_factory.promotion.gating.live_capital_gate import (
    LiveCapitalGate,
)


def test_live_capital_gate_has_no_execution_or_capital_authority():
    gate = LiveCapitalGate()

    forbidden_keywords = [
        "execute",
        "place_order",
        "allocate",
        "deploy",
        "promote",
        "demote",
    ]

    source = inspect.getsource(gate.__class__)

    for word in forbidden_keywords:
        assert word not in source, f"Forbidden authority detected: {word}"
