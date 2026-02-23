from core.strategy_reputation.performance_cycle import PerformanceCycle
from core.strategy_reputation.reputation import compute_strategy_reputation


def test_strategy_reputation_aggregation():
    cycles = [
        PerformanceCycle("s1", "c1", 100.0, 0.1, 1.0, 50),
        PerformanceCycle("s1", "c2", -20.0, 0.2, 0.8, 40),
    ]

    rep = compute_strategy_reputation("s1", cycles)

    assert rep.cycles == 2
    assert rep.total_pnl == 80.0
    assert rep.avg_sharpe == 0.9
    assert rep.worst_drawdown == 0.2
