from core.v2.operator_dashboard.drills.drill_manual_revoke import (
    run_drill_manual_revoke,
)


def test_live_readiness_drill_manual_revoke():
    """
    Automated verification of Drill 2:
    Manual revoke must immediately deny live eligibility.
    """
    run_drill_manual_revoke(
        strategy_id="drill-strategy-2",
        operator="drill-operator",
    )
