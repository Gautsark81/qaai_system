from core.v2.observability.dashboards import ObservabilityDashboardBuilder
from core.v2.observability.contracts import DriftSignal, AlphaDecayReport


def test_dashboard_is_read_only():
    builder = ObservabilityDashboardBuilder()

    snapshot = builder.build(
        strategy_id="S1",
        alpha_verdict="STRONG_ALPHA",
        drift_signals=[
            DriftSignal("ssr", 0.8, 0.7, -0.1, "HIGH")
        ],
        decay=AlphaDecayReport(
            strategy_id="S1",
            half_life_days=10,
            decay_rate=0.05,
            status="DECAYING",
        ),
    )

    assert snapshot.strategy_id == "S1"
    assert "SSR_DRIFT" in snapshot.drift_flags
    assert snapshot.decay_status == "DECAYING"
