from core.v2.observability.decay_analysis import AlphaDecayAnalyzer


def test_decay_detected():
    a = AlphaDecayAnalyzer()
    report = a.analyze(
        strategy_id="S1",
        scores=[0.9, 0.8, 0.7],
        days_between=5,
    )

    assert report.status in ("DECAYING", "CRITICAL")
    assert report.decay_rate > 0
