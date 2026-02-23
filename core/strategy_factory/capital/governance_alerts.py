from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.strategy_factory.capital.governance_drift import (
    CapitalGovernanceDriftReport,
)
from core.strategy_factory.capital.ledger_reconciliation import (
    CapitalUsageReconciliationReport,
)
from core.strategy_factory.capital.reporting import (
    CapitalUsageReport,
)


# ============================================================
# C4.8 — Governance Alert (Immutable)
# ============================================================

@dataclass(frozen=True)
class CapitalGovernanceAlert:
    """
    Immutable governance alert record.

    Properties:
    - Read-only
    - Deterministic
    - No side effects
    """

    alert_type: str


# ============================================================
# C4.8 — Alert Evaluation Engine (Pure)
# ============================================================

def evaluate_capital_governance_alerts(
    *,
    reconciliation: CapitalUsageReconciliationReport,
    drift: CapitalGovernanceDriftReport,
    usage_report: CapitalUsageReport,
) -> List[CapitalGovernanceAlert]:
    """
    Evaluate governance invariants and emit alert records.

    Rules (v1, test-defined):
    - If governance drift exists → emit GOVERNANCE_DRIFT alert
    """

    alerts: List[CapitalGovernanceAlert] = []

    if drift.is_drift:
        alerts.append(
            CapitalGovernanceAlert(
                alert_type="GOVERNANCE_DRIFT"
            )
        )

    return alerts
