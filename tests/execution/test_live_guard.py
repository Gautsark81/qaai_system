import pytest

# ✅ ADD THIS IMPORT
from execution.orchestrator import ExecutionOrchestrator


class DummyOrder:
    def __init__(self, is_live):
        self.is_live = is_live


class DummyRouter:
    def route(self, order):
        return {"status": "ok"}


def test_live_trade_blocked_by_default():
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        config={},
    )

    order = {"is_live": True}

    with pytest.raises(RuntimeError, match="approved_for_live=False"):
        orch.submit_order(order)


def test_paper_trade_allowed_by_default():
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        config={},
    )

    order = {"is_live": False}

    result = orch.submit_order(order)
    assert result["status"] in ("submitted", "filled")


def test_live_trade_allowed_only_if_explicit():
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        config={"approved_for_live": True},
    )

    order = {"is_live": True}

    result = orch.submit_order(order)
    assert result["status"] in ("submitted", "filled")
