from core.capital.allocation_curves.engine import CapitalAllocationCurveEngine
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_curve_engine_advisory_only():
    engine = CapitalAllocationCurveEngine()

    snap = engine.compute(
        lifecycle_state=LifecycleState.LIVE,
        ssr=0.85,
        ssr_status=SSRStatus.STRONG,
        health_score=0.9,
        health_status=HealthStatus.HEALTHY,
    )

    # Advisory snapshot properties
    assert snap.eligible is True
    assert 0.0 < snap.allocation_pct <= 1.0
    assert snap.reason
