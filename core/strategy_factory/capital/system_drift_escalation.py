from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
from typing import List

from execution.execution_reconciler import DriftRecord, DriftSeverity
from core.strategy_factory.capital.ledger_reconciliation import (
    CapitalUsageReconciliationReport,
)


# ============================================================
# ESCALATION LEVEL (NON-EXTENSIBLE)
# ============================================================

class SystemEscalationLevel(Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    SYSTEM_HALT = "system_halt"


# ============================================================
# IMMUTABLE REPORT
# ============================================================

@dataclass(frozen=True)
class SystemDriftEscalationReport:
    level: SystemEscalationLevel
    execution_drifts: int
    capital_violations: int
    governance_violation: bool
    fingerprint: str
    timestamp: str


# ============================================================
# ESCALATION ENGINE
# ============================================================

class SystemDriftEscalationEngine:
    """
    Cross-layer drift escalation binding.

    Guarantees:
    - Deterministic
    - Immutable report
    - No side effects
    - Audit-hash anchored
    """

    def evaluate(
        self,
        *,
        execution_drifts: List[DriftRecord],
        capital_report: CapitalUsageReconciliationReport,
        governance_violation: bool,
    ) -> SystemDriftEscalationReport:

        exec_critical = any(
            d.severity == DriftSeverity.CRITICAL
            for d in execution_drifts
        )

        exec_warning = any(
            d.severity == DriftSeverity.WARNING
            for d in execution_drifts
        )

        capital_inconsistent = not capital_report.is_consistent
        capital_violations = len(capital_report.violations)

        # ----------------------------------------------------
        # Escalation Decision Matrix (STRICT)
        # ----------------------------------------------------

        if governance_violation:
            level = SystemEscalationLevel.SYSTEM_HALT

        elif exec_critical and capital_inconsistent:
            level = SystemEscalationLevel.SYSTEM_HALT

        elif exec_critical or capital_inconsistent:
            level = SystemEscalationLevel.CRITICAL

        elif exec_warning or capital_violations > 0:
            level = SystemEscalationLevel.WARNING

        else:
            level = SystemEscalationLevel.OK

        # ----------------------------------------------------
        # Deterministic fingerprint
        # ----------------------------------------------------

        fingerprint_payload = {
            "execution_drifts": len(execution_drifts),
            "capital_violations": capital_violations,
            "governance_violation": governance_violation,
            "level": level.value,
        }

        payload_str = json.dumps(
            fingerprint_payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        fingerprint = hashlib.sha256(
            payload_str.encode("utf-8")
        ).hexdigest()

        timestamp = datetime.now(timezone.utc).isoformat()

        return SystemDriftEscalationReport(
            level=level,
            execution_drifts=len(execution_drifts),
            capital_violations=capital_violations,
            governance_violation=governance_violation,
            fingerprint=fingerprint,
            timestamp=timestamp,
        )