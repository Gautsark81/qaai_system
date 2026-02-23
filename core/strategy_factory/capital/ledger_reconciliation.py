from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from core.strategy_factory.capital.ledger_models import (
    CapitalLedgerEntry,
    CapitalUsageLedgerEntry,
)
from core.strategy_factory.capital.ledger_aggregation import (
    compute_strategy_capital_balance,
    compute_global_capital_balance,
)

# ============================================================
# LEGACY — Raw Capital Ledger Reconciliation (Pre-C4.5)
# ============================================================

@dataclass(frozen=True)
class CapitalLedgerReconciliationReport:
    """
    Immutable reconciliation result for raw capital ledger.

    Guarantees:
    - Deterministic
    - Order-independent
    - No side effects
    """

    global_balance: float
    per_strategy: Dict[str, float]
    is_consistent: bool


def reconcile_capital_ledger(
    ledger: Iterable[CapitalLedgerEntry],
) -> CapitalLedgerReconciliationReport:
    """
    Reconcile raw capital ledger state.

    Invariants:
    - Uses aggregation functions (single source of truth)
    - Order-independent
    - No mutation
    """

    ledger = list(ledger)

    strategies = {
        entry.strategy_dna
        for entry in ledger
        if entry.strategy_dna is not None
    }

    per_strategy: Dict[str, float] = {
        strategy: compute_strategy_capital_balance(
            strategy_dna=strategy,
            ledger=ledger,
        )
        for strategy in sorted(strategies)
    }

    global_balance = compute_global_capital_balance(ledger)

    summed = sum(per_strategy.values())
    is_consistent = abs(summed - global_balance) < 1e-9

    return CapitalLedgerReconciliationReport(
        global_balance=global_balance,
        per_strategy=per_strategy,
        is_consistent=is_consistent,
    )


# ============================================================
# C4.5 — Capital Usage Ledger Reconciliation (NEW)
# ============================================================

@dataclass(frozen=True)
class CapitalUsageReconciliationReport:
    """
    Immutable reconciliation result for capital usage ledger.

    Guarantees:
    - Deterministic
    - Replay-safe
    - Governance-only
    """

    is_consistent: bool
    violations: List[str]
    entry_count: int


def reconcile_capital_usage_ledger(
    entries: List[CapitalUsageLedgerEntry],
) -> CapitalUsageReconciliationReport:
    """
    Reconcile capital usage ledger entries.

    Enforced invariants:
    - capital_after - capital_before == capital_delta
    - capital_after >= 0
    - source_event_id present
    """

    violations: List[str] = []

    for idx, entry in enumerate(entries):
        if entry.capital_after - entry.capital_before != entry.capital_delta:
            violations.append(
                f"delta_mismatch at index {idx}: "
                f"{entry.capital_after} - {entry.capital_before} "
                f"!= {entry.capital_delta}"
            )

        if entry.capital_after < 0:
            violations.append(
                f"negative_capital at index {idx}: {entry.capital_after}"
            )

        if not entry.source_event_id:
            violations.append(
                f"missing_source_event_id at index {idx}"
            )

    return CapitalUsageReconciliationReport(
        is_consistent=len(violations) == 0,
        violations=violations,
        entry_count=len(entries),
    )
