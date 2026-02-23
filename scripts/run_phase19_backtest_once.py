from datetime import datetime
from intelligence.backtest_adapter import BacktestIntelligenceAdapter


class DummyTrade:
    def __init__(self, r, symbol="TEST", regime="NORMAL"):
        self.net_r = r
        self.symbol = symbol
        self.regime = regime


class DummyRisk:
    def count_blocks(self): return 0
    def count_atr(self): return 0
    def count_size(self): return 0


class DummyExec:
    def avg_slippage(self): return 0.01
    def p95_slippage(self): return 0.02
    def reject_rate(self): return 0.0
    def latency_p95(self): return 120


if __name__ == "__main__":
    adapter = BacktestIntelligenceAdapter()
    trades = [DummyTrade(1.0), DummyTrade(-0.5), DummyTrade(2.0)]
    snapshot, _, _ = adapter.process_backtest(
        strategy_id="STRAT_ALPHA",
        strategy_version="1.0",
        trades=trades,
        risk_events=DummyRisk(),
        execution_stats=DummyExec(),
        window_start=datetime(2023, 1, 1),
        window_end=datetime(2023, 12, 31),
    )
    print("Phase-19 snapshot written:", snapshot.strategy_id)
