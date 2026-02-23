from datetime import datetime

from core.strategy_factory.capital.ledger_models import (
    CapitalLedgerEntry,
    CapitalLedgerEventType,
)
from core.strategy_factory.capital.ledger_aggregation import (
    compute_strategy_capital_balance,
    compute_global_capital_balance,
)


def _e(
    *,
    strategy: str,
    event: CapitalLedgerEventType,
    amount: float,
):
    return CapitalLedgerEntry(
        entry_id=f"{strategy}-{event}",
        strategy_dna=strategy,
        event_type=event,
        amount=amount,
        source_event_fingerprint="src",
        created_at=datetime(2025, 1, 1),
        notes=None,
        fingerprint=f"fp-{strategy}-{event}",
    )


# ============================================================
# C3.6-B-T1 — Single strategy balance
# ============================================================

def test_strategy_capital_balance_simple():
    ledger = [
        _e(strategy="S1", event=CapitalLedgerEventType.ALLOCATION_APPROVED, amount=50_000),
        _e(strategy="S1", event=CapitalLedgerEventType.CAPITAL_RELEASED, amount=10_000),
    ]

    balance = compute_strategy_capital_balance(
        strategy_dna="S1",
        ledger=ledger,
    )

    assert balance == 40_000


# ============================================================
# C3.6-B-T2 — Ignores other strategies
# ============================================================

def test_strategy_balance_ignores_other_strategies():
    ledger = [
        _e(strategy="S1", event=CapitalLedgerEventType.ALLOCATION_APPROVED, amount=30_000),
        _e(strategy="S2", event=CapitalLedgerEventType.ALLOCATION_APPROVED, amount=99_000),
    ]

    balance = compute_strategy_capital_balance(
        strategy_dna="S1",
        ledger=ledger,
    )

    assert balance == 30_000


# ============================================================
# C3.6-B-T3 — Denials do not affect balance
# ============================================================

def test_denied_allocation_has_no_effect():
    ledger = [
        _e(strategy="S1", event=CapitalLedgerEventType.ALLOCATION_DENIED, amount=100_000),
        _e(strategy="S1", event=CapitalLedgerEventType.ALLOCATION_APPROVED, amount=20_000),
    ]

    balance = compute_strategy_capital_balance(
        strategy_dna="S1",
        ledger=ledger,
    )

    assert balance == 20_000


# ============================================================
# C3.6-B-T4 — Adjustments apply signed values
# ============================================================

def test_capital_adjustment_applies_signed_amount():
    ledger = [
        _e(strategy="S1", event=CapitalLedgerEventType.ALLOCATION_APPROVED, amount=50_000),
        _e(strategy="S1", event=CapitalLedgerEventType.CAPITAL_ADJUSTED, amount=-5_000),
    ]

    balance = compute_strategy_capital_balance(
        strategy_dna="S1",
        ledger=ledger,
    )

    assert balance == 45_000


# ============================================================
# C3.6-B-T5 — Global capital balance
# ============================================================

def test_global_capital_balance():
    ledger = [
        _e(strategy="S1", event=CapitalLedgerEventType.ALLOCATION_APPROVED, amount=40_000),
        _e(strategy="S2", event=CapitalLedgerEventType.ALLOCATION_APPROVED, amount=60_000),
        _e(strategy="S1", event=CapitalLedgerEventType.CAPITAL_RELEASED, amount=10_000),
    ]

    total = compute_global_capital_balance(ledger)

    assert total == 90_000
