from datetime import datetime
from intelligence.backtest_adapter import BacktestIntelligenceAdapter


class DummyTrade:
    def __init__(self, net_r, closed=True):
        self.net_r = net_r
        self.is_closed = closed
        self.symbol = "TEST"
        self.regime = "NORMAL"


class DummyRiskEvents:
    def count_blocks(self): return 0
    def count_atr(self): return 0
    def count_size(self): return 0


class DummyExecutionStats:
    def avg_slippage(self): return 0.01
    def p95_slippage(self): return 0.02
    def reject_rate(self): return 0.0
    def latency_p95(self): return 120


def test_phase19_snapshot_emitted_from_backtest():
    """
    CI invariant:
    Every completed backtest MUST emit a Phase-19 snapshot.
    """

    adapter = BacktestIntelligenceAdapter()

    trades = [
        DummyTrade(1.0),
        DummyTrade(-0.5),
        DummyTrade(2.0),
    ]

    snapshot, symbol_metrics, regime_metrics = adapter.process_backtest(
        strategy_id="TEST_STRATEGY",
        strategy_version="1.0.0",
        trades=trades,
        risk_events=DummyRiskEvents(),
        execution_stats=DummyExecutionStats(),
        window_start=datetime(2023, 1, 1),
        window_end=datetime(2023, 12, 31),
    )

    # 🔒 Core invariants
    assert snapshot.total_trades == 3
    assert snapshot.successful_trades == 2
    assert snapshot.ssr > 0.0

    # 🔒 Intelligence completeness
    assert "TEST" in symbol_metrics
    assert "NORMAL" in regime_metrics
