from __future__ import annotations

from decimal import Decimal
from typing import Iterable, List

from core.strategy_factory.capital.ledger_models import (
    CapitalLedgerEntry,
    CapitalLedgerEventType,
    CapitalUsageLedgerEntry,
)
from core.strategy_factory.capital.event_models import CapitalEventAudit


# ============================================================
# Internal helper — signed capital impact
# ============================================================

def _ledger_entry_impact(entry: CapitalLedgerEntry) -> float:
    """
    Compute signed capital impact for a single ledger entry.

    HARD LAW (test-enforced):
    - APPROVED   → +amount
    - ADJUSTED   → +amount (signed)
    - RELEASED   → -amount
    - DENIED     → 0
    """

    if entry.event_type == CapitalLedgerEventType.ALLOCATION_APPROVED:
        return float(entry.amount)

    if entry.event_type == CapitalLedgerEventType.CAPITAL_ADJUSTED:
        return float(entry.amount)

    if entry.event_type == CapitalLedgerEventType.CAPITAL_RELEASED:
        return -float(entry.amount)

    if entry.event_type == CapitalLedgerEventType.ALLOCATION_DENIED:
        return 0.0

    raise ValueError(f"Unsupported ledger event type: {entry.event_type}")


# ============================================================
# C3.6-B — Per-strategy aggregation
# ============================================================

def compute_strategy_capital_balance(
    *,
    strategy_dna: str,
    ledger: Iterable[CapitalLedgerEntry],
) -> float:
    """
    Compute net allocated capital for a single strategy.

    Properties:
    - Deterministic
    - Ignores other strategies
    - Order-independent
    """

    total = 0.0

    for entry in ledger:
        if entry.strategy_dna != strategy_dna:
            continue

        total += _ledger_entry_impact(entry)

    return total


# ============================================================
# C3.6-B — Global aggregation
# ============================================================

def compute_global_capital_balance(
    ledger: Iterable[CapitalLedgerEntry],
) -> float:
    """
    Compute total allocated capital across all strategies.

    Properties:
    - Deterministic
    - Strategy-agnostic
    """

    total = 0.0

    for entry in ledger:
        total += _ledger_entry_impact(entry)

    return total


# ============================================================
# C4.4 — Capital Usage Ledger (NEW, GOVERNED)
# ============================================================

def build_capital_usage_ledger(
    events: Iterable[CapitalEventAudit],
) -> List[CapitalUsageLedgerEntry]:
    """
    Build a deterministic, append-only capital usage ledger
    from capital audit events.

    Governance guarantees:
    - Pure function
    - No mutation of source events
    - One ledger entry per audit event
    - Deterministic ordering
    """

    ledger: List[CapitalUsageLedgerEntry] = []

    for event in events:
        # Capital before / after derived strictly from memory
        capital_before = (
            Decimal(str(event.memory_before.cumulative_allocated))
            if event.memory_before
            else Decimal("0")
        )

        capital_after = Decimal(str(event.memory_after.cumulative_allocated))

        ledger.append(
            CapitalUsageLedgerEntry(
                ledger_id=event.fingerprint,
                timestamp_utc=event.created_at,
                trading_day=event.created_at.date(),
                source_event_id=event.fingerprint,
                source_event_type="ALLOCATION",
                scope="STRATEGY",
                scope_id=event.strategy_dna,
                capital_before=capital_before,
                capital_after=capital_after,
                capital_delta=capital_after - capital_before,
                reason=getattr(event.allocation, "reason", ""),
            )
        )

    # Deterministic ordering (replay-safe)
    ledger.sort(key=lambda e: (e.timestamp_utc, e.ledger_id))

    return ledger
