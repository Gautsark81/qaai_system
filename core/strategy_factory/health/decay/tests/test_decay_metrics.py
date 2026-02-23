from core.strategy_factory.health.decay.decay_metrics import DecayMetrics


def test_composite_score_bounds():
    m = DecayMetrics(0.5, 0.5, 0.5, 0.5)
    score = m.composite()
    assert 0.0 <= score <= 1.0
