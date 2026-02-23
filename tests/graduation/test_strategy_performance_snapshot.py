from domain.graduation.strategy_performance_snapshot import (
    StrategyPerformanceSnapshot
)


def test_strategy_performance_snapshot():
    s = StrategyPerformanceSnapshot("S1", 0.82, 0.06, 45, 320)
    assert s.ssr > 0.8
