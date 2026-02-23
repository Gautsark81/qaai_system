from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.strategy_factory.capital.ledger_reconciliation import (
    CapitalUsageReconciliationReport,
)


# ============================================================
# C4.6 — Governance Drift Report (Immutable)
# ============================================================

@dataclass(frozen=True)
class CapitalGovernanceDriftReport:
    """
    Immutable governance drift detection result.

    Properties:
    - Read-only
    - Deterministic
    - No enforcement
    """

    is_drift: bool
    inconsistent_count: int


# ============================================================
# C4.6 — Drift Detection Engine (Pure)
# ============================================================

def detect_capital_governance_drift(
    reports: Iterable[CapitalUsageReconciliationReport],
) -> CapitalGovernanceDriftReport:
    """
    Detect governance drift from reconciliation reports.

    Drift rule (v1, test-defined):
    - Drift exists if 2 or more reports are inconsistent.
    """

    reports = list(reports)

    inconsistent_count = sum(
        1 for r in reports if not r.is_consistent
    )

    return CapitalGovernanceDriftReport(
        is_drift=inconsistent_count >= 2,
        inconsistent_count=inconsistent_count,
    )
