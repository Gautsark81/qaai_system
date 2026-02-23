from core.v2.operator_dashboard.drills.drill_divergence_breach import (
    run_drill_divergence_breach,
)


def test_live_readiness_drill_divergence_breach():
    """
    Automated verification of Drill 4:
    Divergence breach must deny live eligibility automatically.
    """
    run_drill_divergence_breach(
        strategy_id="drill-strategy-4",
        operator="drill-operator",
    )
