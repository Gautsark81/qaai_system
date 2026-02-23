import pytest
from qaai_system.execution.execution_engine import ExecutionEngine


def test_paper_mode_is_default_safe():
    engine = ExecutionEngine(mode="paper")
    resp = engine.submit({"symbol": "NIFTY", "quantity": 1})
    assert resp["mode"] == "paper"


def test_live_mode_blocked_by_default():
    engine = ExecutionEngine(mode="live")
    with pytest.raises(RuntimeError):
        engine.submit({"symbol": "NIFTY", "quantity": 1})


def test_idempotency_blocks_duplicates():
    engine = ExecutionEngine(mode="paper")
    order = {"symbol": "NIFTY", "quantity": 1}

    r1 = engine.submit(order)
    r2 = engine.submit(order)

    assert r1["status"] == "ok"
    assert r2["status"] == "duplicate"
