from core.strategy_factory.promotion.gating.tiny_live_gate import (
    TinyLiveGate,
)


def test_tiny_live_gate_has_no_side_effects():
    gate = TinyLiveGate()

    forbidden = [
        "execute",
        "order",
        "broker",
        "capital",
        "arm",
        "deploy",
    ]

    for attr in forbidden:
        assert not hasattr(gate, attr)
