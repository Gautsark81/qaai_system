from __future__ import annotations

from core.strategy_factory.capital.governance_drift import (
    CapitalGovernanceDriftReport,
)
from core.strategy_factory.capital.ledger_reconciliation import (
    CapitalUsageReconciliationReport,
)
from core.strategy_factory.capital.reporting import (
    CapitalUsageReport,
)
from core.strategy_factory.capital.governance_alerts import (
    evaluate_capital_governance_alerts,
)


def test_governance_drift_raises_alert():
    """
    C4.8 — Governance drift must raise a GOVERNANCE_DRIFT alert.

    This is read-only and produces alert records only.
    """

    reconciliation = CapitalUsageReconciliationReport(
        is_consistent=False,
        violations=["delta_mismatch"],
        entry_count=3,
    )

    drift = CapitalGovernanceDriftReport(
        is_drift=True,
        inconsistent_count=2,
    )

    usage_report = CapitalUsageReport(
        entry_count=3,
        total_allocated=150.0,
        total_released=40.0,
    )

    alerts = evaluate_capital_governance_alerts(
        reconciliation=reconciliation,
        drift=drift,
        usage_report=usage_report,
    )

    assert len(alerts) == 1
    assert alerts[0].alert_type == "GOVERNANCE_DRIFT"
