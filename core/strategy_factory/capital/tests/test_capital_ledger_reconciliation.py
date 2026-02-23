from core.strategy_factory.capital.ledger_models import (
    CapitalLedgerEntry,
    CapitalLedgerEventType,
)
from core.strategy_factory.capital.ledger_aggregation import (
    compute_strategy_capital_balance,
    compute_global_capital_balance,
)
from core.strategy_factory.capital.ledger_reconciliation import (
    reconcile_capital_ledger,
)


def _e(strategy, event, amount):
    return CapitalLedgerEntry(
        strategy_dna=strategy,
        event_type=event,
        amount=amount,
    )


# ============================================================
# C3.6-C-T1 — Empty ledger is consistent
# ============================================================

def test_empty_ledger_is_consistent():
    report = reconcile_capital_ledger([])

    assert report.global_balance == 0.0
    assert report.per_strategy == {}
    assert report.is_consistent is True


# ============================================================
# C3.6-C-T2 — Strategy sums equal global sum
# ============================================================

def test_strategy_balances_match_global_balance():
    ledger = [
        _e("A", CapitalLedgerEventType.ALLOCATION_APPROVED, 100),
        _e("B", CapitalLedgerEventType.ALLOCATION_APPROVED, 200),
        _e("A", CapitalLedgerEventType.CAPITAL_RELEASED, 40),
    ]

    report = reconcile_capital_ledger(ledger)

    assert report.per_strategy["A"] == 60
    assert report.per_strategy["B"] == 200
    assert report.global_balance == 260
    assert report.is_consistent is True


# ============================================================
# C3.6-C-T3 — Order does not matter
# ============================================================

def test_ledger_reconciliation_is_order_independent():
    ledger1 = [
        _e("A", CapitalLedgerEventType.ALLOCATION_APPROVED, 100),
        _e("A", CapitalLedgerEventType.CAPITAL_RELEASED, 20),
    ]

    ledger2 = list(reversed(ledger1))

    r1 = reconcile_capital_ledger(ledger1)
    r2 = reconcile_capital_ledger(ledger2)

    assert r1 == r2


# ============================================================
# C3.6-C-T4 — Reconciliation uses aggregation logic (not reimplementation)
# ============================================================

def test_reconciliation_matches_aggregation_functions():
    ledger = [
        _e("X", CapitalLedgerEventType.ALLOCATION_APPROVED, 300),
        _e("X", CapitalLedgerEventType.CAPITAL_ADJUSTED, -50),
        _e("Y", CapitalLedgerEventType.ALLOCATION_APPROVED, 100),
    ]

    report = reconcile_capital_ledger(ledger)

    assert report.per_strategy["X"] == compute_strategy_capital_balance(
        strategy_dna="X",
        ledger=ledger,
    )

    assert report.global_balance == compute_global_capital_balance(ledger)
