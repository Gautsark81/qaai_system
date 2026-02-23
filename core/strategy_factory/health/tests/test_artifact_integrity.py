def test_health_report_immutable():
    from core.strategy_factory.health.artifacts import HealthReport
    from core.strategy_factory.health.snapshot import StrategyHealthSnapshot
    from datetime import datetime

    snap = StrategyHealthSnapshot(
        strategy_dna="x",
        timestamp=datetime.utcnow(),
        health_score=0.5,
        confidence=0.5,
        decay_risk=0.2,
        performance_metrics={},
        risk_metrics={},
        signal_metrics={},
        regime_alignment={},
        flags=[],
    )

    report = HealthReport(snapshot=snap, inputs_hash="abc")

    assert report.version == "11.2"
