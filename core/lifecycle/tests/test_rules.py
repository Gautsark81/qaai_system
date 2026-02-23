from datetime import datetime, timedelta

from core.lifecycle.rules import LifecycleRules
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_candidate_to_paper():
    rules = LifecycleRules()
    now = datetime.utcnow()

    state, reason = rules.evaluate(
        current_state=LifecycleState.CANDIDATE,
        since=now - timedelta(days=1),
        now=now,
        ssr_status=SSRStatus.STABLE,
        health_status=HealthStatus.HEALTHY,
    )

    assert state == LifecycleState.PAPER


def test_paper_to_live_requires_time_and_health():
    rules = LifecycleRules(min_live_days=3)
    now = datetime.utcnow()

    state, _ = rules.evaluate(
        current_state=LifecycleState.PAPER,
        since=now - timedelta(days=5),
        now=now,
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert state == LifecycleState.LIVE


def test_live_to_degraded_on_weak_ssr():
    rules = LifecycleRules()
    now = datetime.utcnow()

    state, _ = rules.evaluate(
        current_state=LifecycleState.LIVE,
        since=now - timedelta(days=10),
        now=now,
        ssr_status=SSRStatus.WEAK,
        health_status=HealthStatus.HEALTHY,
    )

    assert state == LifecycleState.DEGRADED


def test_degraded_to_retired_on_failing_ssr():
    rules = LifecycleRules()
    now = datetime.utcnow()

    state, _ = rules.evaluate(
        current_state=LifecycleState.DEGRADED,
        since=now - timedelta(days=10),
        now=now,
        ssr_status=SSRStatus.FAILING,
        health_status=HealthStatus.HEALTHY,
    )

    assert state == LifecycleState.RETIRED


def test_operator_override_dominates():
    rules = LifecycleRules()
    now = datetime.utcnow()

    state, reason = rules.evaluate(
        current_state=LifecycleState.LIVE,
        since=now,
        now=now,
        ssr_status=SSRStatus.FAILING,
        health_status=HealthStatus.CRITICAL,
        operator_override=LifecycleState.RETIRED,
    )

    assert state == LifecycleState.RETIRED
