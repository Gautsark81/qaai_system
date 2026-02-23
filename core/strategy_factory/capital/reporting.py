from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.strategy_factory.capital.ledger_models import CapitalUsageLedgerEntry


# ============================================================
# C4.7 — Capital Usage Report (Immutable)
# ============================================================

@dataclass(frozen=True)
class CapitalUsageReport:
    """
    Immutable, audit-safe capital usage summary.

    Properties:
    - Read-only
    - Deterministic
    - No side effects
    """

    entry_count: int
    total_allocated: float
    total_released: float


# ============================================================
# C4.7 — Reporting Builder (Pure)
# ============================================================

def build_capital_usage_report(
    entries: Iterable[CapitalUsageLedgerEntry],
) -> CapitalUsageReport:
    """
    Build a deterministic summary report from capital usage ledger entries.

    Rules (v1, test-defined):
    - entry_count = number of entries
    - total_allocated = sum of positive capital_delta
    - total_released = absolute sum of negative capital_delta
    """

    total_allocated = 0.0
    total_released = 0.0
    count = 0

    for entry in entries:
        count += 1

        if entry.capital_delta > 0:
            total_allocated += float(entry.capital_delta)
        elif entry.capital_delta < 0:
            total_released += abs(float(entry.capital_delta))

    return CapitalUsageReport(
        entry_count=count,
        total_allocated=total_allocated,
        total_released=total_released,
    )
