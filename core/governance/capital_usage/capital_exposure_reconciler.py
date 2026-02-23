from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from .capital_usage_ledger import CapitalUsageLedger


# ---------------------------------------------------------------------
# Immutable Reconciliation State
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CapitalExposureState:
    strategy_id: str
    governance_id: str
    allocated_capital: float
    deployed_capital: float
    realized_pnl: float
    utilization_ratio: float
    over_allocated: bool
    last_updated_at: datetime


# ---------------------------------------------------------------------
# Deterministic Reconciler
# ---------------------------------------------------------------------


class CapitalExposureReconciler:
    """
    Phase C5.2 — Capital Exposure Reconciliation

    Guarantees:
    - Deterministic replay
    - Timestamp arbitration (latest wins)
    - Over-allocation detection
    - Pure functional behavior
    """

    def reconcile(
        self,
        *,
        ledger: CapitalUsageLedger,
        strategy_id: str,
        governance_id: str,
    ) -> CapitalExposureState:

        entries = [
            e
            for e in ledger.entries()
            if e.strategy_id == strategy_id
            and e.governance_id == governance_id
        ]

        if not entries:
            raise ValueError("No capital usage entries found")

        # Last timestamp wins
        latest = max(entries, key=lambda e: e.timestamp)

        allocated = latest.allocated_capital
        deployed = latest.deployed_capital

        utilization = deployed / allocated if allocated > 0 else 0.0
        over_allocated = deployed > allocated

        return CapitalExposureState(
            strategy_id=strategy_id,
            governance_id=governance_id,
            allocated_capital=allocated,
            deployed_capital=deployed,
            realized_pnl=latest.realized_pnl,
            utilization_ratio=utilization,
            over_allocated=over_allocated,
            last_updated_at=latest.timestamp,
        )