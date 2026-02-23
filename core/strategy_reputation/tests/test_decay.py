from core.strategy_reputation.performance_cycle import PerformanceCycle
from core.strategy_reputation.decay import (
    compute_decayed_score,
    compute_decay_immunity_factor,
    compute_time_resilient_score,
)


def test_recent_cycles_weight_more():
    cycles = [
        PerformanceCycle("s1", "c1", 100.0, 0.1, 1.0, 10),
        PerformanceCycle("s1", "c2", -50.0, 0.2, 0.8, 10),
    ]

    score = compute_decayed_score(cycles, half_life_cycles=1.0)

    assert score < 100.0
    assert score > -50.0


def test_immunity_increases_with_cycles():
    low = compute_decay_immunity_factor(1)
    mid = compute_decay_immunity_factor(3)
    high = compute_decay_immunity_factor(10)

    assert low < mid < high
    assert high <= 1.5


def test_long_career_more_resilient():
    cycles = [
        PerformanceCycle("s1", f"c{i}", 50.0, 0.1, 1.0, 10)
        for i in range(6)
    ] + [
        PerformanceCycle("s1", "c_bad", -200.0, 0.5, -1.5, 10)
    ]

    score = compute_time_resilient_score("s1", cycles)

    assert score > -50.0
