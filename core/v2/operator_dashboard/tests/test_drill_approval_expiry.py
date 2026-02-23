from core.v2.operator_dashboard.drills.drill_approval_expiry import (
    run_drill_approval_expiry,
)


def test_live_readiness_drill_approval_expiry():
    """
    Automated verification of Drill 1:
    Approval must expire without operator action.
    """
    run_drill_approval_expiry(
        strategy_id="drill-strategy-1",
        operator="drill-operator",
        ttl_seconds=5,  # short TTL for test
    )
