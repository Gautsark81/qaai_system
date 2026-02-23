from core.strategy_reputation.performance_cycle import PerformanceCycle
from core.strategy_reputation.normalization import normalize_strategy_reputation


def test_single_cycle_low_confidence():
    cycles = [
        PerformanceCycle("s1", "c1", 100.0, 0.1, 3.0, 20),
    ]

    norm = normalize_strategy_reputation("s1", cycles)

    assert norm.confidence < 0.5
    assert norm.normalized_score < 100.0


def test_consistent_multi_cycle_rewarded():
    cycles = [
        PerformanceCycle("s1", "c1", 40.0, 0.1, 1.2, 50),
        PerformanceCycle("s1", "c2", 45.0, 0.1, 1.1, 55),
        PerformanceCycle("s1", "c3", 42.0, 0.1, 1.15, 52),
    ]

    norm = normalize_strategy_reputation("s1", cycles)

    assert norm.confidence > 0.5
    assert norm.stability_penalty < 0.3
    assert norm.normalized_score > 20.0


def test_lucky_but_volatile_penalized():
    cycles = [
        PerformanceCycle("s1", "c1", 200.0, 0.5, 3.5, 10),
        PerformanceCycle("s1", "c2", -150.0, 0.6, -2.0, 8),
    ]

    norm = normalize_strategy_reputation("s1", cycles)

    assert norm.stability_penalty > 0.5
    assert norm.normalized_score < 50.0
