from datetime import datetime
from intelligence.paper_adapter import PaperTradingIntelligenceAdapter


class DummyTrade:
    def __init__(self, net_r, closed=True):
        self.net_r = net_r
        self.is_closed = closed
        self.symbol = "PAPER"
        self.regime = "NORMAL"


class DummyRiskEvents:
    def count_blocks(self): return 0
    def count_atr(self): return 0
    def count_size(self): return 0


class DummyExecutionStats:
    def avg_slippage(self): return 0.01
    def p95_slippage(self): return 0.02
    def reject_rate(self): return 0.0
    def latency_p95(self): return 110


def test_phase19_snapshot_emitted_from_paper_trading():
    adapter = PaperTradingIntelligenceAdapter()

    trades = [
        DummyTrade(1.0),
        DummyTrade(-0.4),
        DummyTrade(1.6),
    ]

    snapshot, symbol_metrics, regime_metrics = adapter.process_paper_trades(
        strategy_id="PAPER_STRAT",
        strategy_version="2.0.0",
        trades=trades,
        risk_events=DummyRiskEvents(),
        execution_stats=DummyExecutionStats(),
        window_start=datetime(2024, 1, 1),
        window_end=datetime(2024, 2, 1),
    )

    # 🔒 Core invariants
    assert snapshot.stage == "PAPER"
    assert snapshot.window_type == "ROLLING"
    assert snapshot.ssr > 0.0

    # 🔒 Intelligence completeness
    assert "PAPER" in symbol_metrics
    assert "NORMAL" in regime_metrics
