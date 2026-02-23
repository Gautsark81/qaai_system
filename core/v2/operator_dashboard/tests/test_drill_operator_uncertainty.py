from core.v2.operator_dashboard.drills.drill_operator_uncertainty import (
    run_drill_operator_uncertainty,
)


def test_live_readiness_drill_operator_uncertainty():
    """
    Automated verification of Drill 5:
    Operator uncertainty must result in HALT-FIRST behavior.
    """
    run_drill_operator_uncertainty(
        strategy_id="drill-strategy-5",
        operator="drill-operator",
    )
