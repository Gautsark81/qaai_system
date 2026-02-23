from datetime import datetime
from core.regime.contracts import RegimeState
from core.regime.stack import RegimeStack


def test_stack_snapshot():
    stack = RegimeStack()
    state = RegimeState(
        timeframe="15m",
        taxonomy={"trend": "RANGE"},
        confidence=0.7,
        persistence=0.6,
        transition_probability=0.4,
        timestamp=datetime.utcnow(),
    )
    stack.update(state)
    snap = stack.snapshot()
    assert "15m" in snap
