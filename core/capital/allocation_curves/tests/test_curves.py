from core.capital.allocation_curves.engine import CapitalAllocationCurveEngine
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_live_allocation_positive():
    engine = CapitalAllocationCurveEngine()

    snap = engine.compute(
        lifecycle_state=LifecycleState.LIVE,
        ssr=0.8,
        ssr_status=SSRStatus.STRONG,
        health_score=0.9,
        health_status=HealthStatus.HEALTHY,
    )

    assert snap.eligible is True
    assert snap.allocation_pct > 0.5


def test_degraded_throttle():
    engine = CapitalAllocationCurveEngine()

    live = engine.compute(
        lifecycle_state=LifecycleState.LIVE,
        ssr=0.9,
        ssr_status=SSRStatus.STRONG,
        health_score=0.9,
        health_status=HealthStatus.HEALTHY,
    )

    degraded = engine.compute(
        lifecycle_state=LifecycleState.DEGRADED,
        ssr=0.9,
        ssr_status=SSRStatus.STRONG,
        health_score=0.9,
        health_status=HealthStatus.HEALTHY,
    )

    assert degraded.allocation_pct < live.allocation_pct


def test_failing_blocks_allocation():
    engine = CapitalAllocationCurveEngine()

    snap = engine.compute(
        lifecycle_state=LifecycleState.LIVE,
        ssr=0.2,
        ssr_status=SSRStatus.FAILING,
        health_score=0.9,
        health_status=HealthStatus.HEALTHY,
    )

    assert snap.allocation_pct == 0.0
    assert snap.eligible is False
