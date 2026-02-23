from __future__ import annotations

from core.strategy_factory.capital.ledger_reconciliation import (
    CapitalUsageReconciliationReport,
)
from core.strategy_factory.capital.governance_drift import (
    detect_capital_governance_drift,
)


def test_governance_drift_detected_on_repeated_inconsistency():
    """
    C4.6 — Governance drift exists if multiple reconciliation
    reports are inconsistent.

    This is a read-only analytical signal.
    """

    reports = [
        CapitalUsageReconciliationReport(
            is_consistent=False,
            violations=["delta_mismatch"],
            entry_count=3,
        ),
        CapitalUsageReconciliationReport(
            is_consistent=False,
            violations=["negative_capital"],
            entry_count=2,
        ),
    ]

    drift = detect_capital_governance_drift(reports)

    assert drift.is_drift is True
    assert drift.inconsistent_count == 2
