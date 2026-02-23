# tests/test_orchestrator_feedback_pnl.py

from qaai_system.execution.orchestrator import ExecutionOrchestrator
from qaai_system.execution.paper_provider import PaperExecutionProvider
from qaai_system.execution.router import ExecutionRouter


class DummyMeta:
    """
    Mock feedback object to capture trades passed from the orchestrator.
    """

    def __init__(self):
        self.trades = []

    def on_trade(self, trade):
        self.trades.append(trade)


def test_feedback_receives_realized_pnl_fifo():
    provider = PaperExecutionProvider(pm_method="fifo")
    feedback = DummyMeta()
    router = ExecutionRouter(provider)
    orch = ExecutionOrchestrator(provider, router, feedback)

    # Simulate buy at $10
    provider.submit_order({"symbol": "Z", "qty": 100, "side": "buy", "price": 10.0})

    # Simulate sell at $12
    provider.submit_order({"symbol": "Z", "qty": 100, "side": "sell", "price": 12.0})

    # Poll to generate feedback and calculate PnL
    orch.poll()

    # Assert feedback contains one trade with correct PnL
    assert len(feedback.trades) == 1
    trade = feedback.trades[0]
    assert trade["symbol"] == "Z"
    assert trade["qty"] == 100
    assert trade["side"] == "sell"
    assert trade["price"] == 12.0
    assert trade["pnl"] == 200.0  # 100 shares * $2 gain
