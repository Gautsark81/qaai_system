from core.v2.operator_dashboard.drills.drill_lifecycle_decay import (
    run_drill_lifecycle_decay,
)


def test_live_readiness_drill_lifecycle_decay():
    """
    Automated verification of Drill 3:
    Lifecycle decay must override approval.
    """
    run_drill_lifecycle_decay(
        strategy_id="drill-strategy-3",
        operator="drill-operator",
    )
