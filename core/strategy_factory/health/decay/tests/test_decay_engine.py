from core.strategy_factory.health.decay import AlphaDecayDetector, AlphaDecayState


def test_decay_report_structure():
    detector = AlphaDecayDetector()

    telemetry = {
        "performance_decay": 0.6,
        "stability_decay": 0.4,
        "consistency_decay": 0.5,
        "regime_decay": 0.3,
    }

    report = detector.evaluate("strat_001", telemetry)

    assert report.strategy_id == "strat_001"
    assert isinstance(report.score, float)
    assert report.state in AlphaDecayState
    assert 0.0 <= report.confidence <= 1.0
