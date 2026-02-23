import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from core.strategy_factory.capital.ledger_models import (
    CapitalLedgerEntry,
    CapitalLedgerEventType,
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _make_entry(
    *,
    amount: float = 50_000,
    event_type: CapitalLedgerEventType = CapitalLedgerEventType.ALLOCATION_APPROVED,
):
    ts = datetime(2025, 1, 1, tzinfo=timezone.utc)

    return CapitalLedgerEntry(
        entry_id="LEDGER-001",
        strategy_dna="STRAT-001",
        event_type=event_type,
        amount=amount,
        source_event_fingerprint="SRC-FP-123",
        created_at=ts,
        notes="test entry",
        fingerprint="LEDGER-FP-ABC",
    )


# ============================================================
# C3.6-A-T1 — Ledger entry is immutable
# ============================================================

def test_ledger_entry_is_immutable():
    entry = _make_entry()

    with pytest.raises(FrozenInstanceError):
        entry.amount = 999_999


# ============================================================
# C3.6-A-T2 — Ledger entry is deterministic
# ============================================================

def test_ledger_entry_is_deterministic():
    entry1 = _make_entry()
    entry2 = _make_entry()

    assert entry1 == entry2


# ============================================================
# C3.6-A-T3 — Zero-amount entries are allowed (denials / no-op)
# ============================================================

def test_ledger_entry_allows_zero_amount():
    entry = _make_entry(
        amount=0.0,
        event_type=CapitalLedgerEventType.ALLOCATION_DENIED,
    )

    assert entry.amount == 0.0
    assert entry.event_type == CapitalLedgerEventType.ALLOCATION_DENIED


# ============================================================
# C3.6-A-T4 — Event type must be a valid enum
# ============================================================

def test_ledger_entry_rejects_invalid_event_type():
    ts = datetime(2025, 1, 1, tzinfo=timezone.utc)

    with pytest.raises(ValueError):
        CapitalLedgerEntry(
            entry_id="LEDGER-002",
            strategy_dna="STRAT-002",
            event_type="INVALID_EVENT",  # ❌ must be enum
            amount=10_000,
            source_event_fingerprint="SRC-FP-999",
            created_at=ts,
            notes=None,
            fingerprint="LEDGER-FP-XYZ",
        )
