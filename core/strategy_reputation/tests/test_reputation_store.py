from core.strategy_reputation.reputation_store import StrategyReputationStore
from core.strategy_reputation.performance_cycle import PerformanceCycle


def test_append_only_store():
    store = StrategyReputationStore()

    c = PerformanceCycle("s1", "c1", 100.0, 0.1, 1.2, 50)
    store.append(c)

    assert len(store.all_cycles()) == 1
    assert store.cycles_for_strategy("s1")[0] == c
