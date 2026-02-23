from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, date
from enum import Enum
from typing import Optional
from decimal import Decimal
import hashlib
import json
import uuid


# ============================================================
# Ledger Event Types (C3.x — FROZEN)
# ============================================================

class CapitalLedgerEventType(str, Enum):
    ALLOCATION_APPROVED = "allocation_approved"
    ALLOCATION_DENIED = "allocation_denied"
    CAPITAL_RELEASED = "capital_released"
    CAPITAL_ADJUSTED = "capital_adjusted"


# ============================================================
# Capital Ledger Entry (C3.x — FROZEN)
# ============================================================

@dataclass(frozen=True)
class CapitalLedgerEntry:
    """
    Immutable capital ledger entry.

    Supports:
    - Explicit fingerprints (tests, replay)
    - Deterministic auto-fingerprint (production)
    - Governance-safe validation
    """

    # Core economics
    strategy_dna: Optional[str]
    event_type: CapitalLedgerEventType
    amount: float

    # Audit metadata
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_event_fingerprint: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc)
    )
    notes: Optional[str] = None

    # Fingerprint (injectable OR computed)
    fingerprint: Optional[str] = None

    def __post_init__(self):
        # --------------------------------------------------
        # Validate event type
        # --------------------------------------------------
        if not isinstance(self.event_type, CapitalLedgerEventType):
            raise ValueError(f"Invalid ledger event type: {self.event_type}")

        # --------------------------------------------------
        # Compute fingerprint if not provided
        # --------------------------------------------------
        if self.fingerprint is None:
            payload = {
                "strategy_dna": self.strategy_dna,
                "event_type": self.event_type.value,
                "amount": self.amount,
                "source_event_fingerprint": self.source_event_fingerprint,
                "created_at": self.created_at.isoformat(),
                "notes": self.notes,
            }

            digest = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode("utf-8")
            ).hexdigest()

            object.__setattr__(self, "fingerprint", digest)


# ============================================================
# C4.4 — Capital Usage Ledger Entry (NEW, GOVERNED)
# ============================================================

@dataclass(frozen=True)
class CapitalUsageLedgerEntry:
    """
    C4.4 — Immutable capital usage ledger entry.

    Purpose:
    - Projection of capital AUDIT events
    - Append-only
    - Replay-safe
    - Deterministic

    NOTE:
    - This does NOT replace CapitalLedgerEntry
    - This does NOT affect execution or allocation
    - This is pure accounting
    """

    ledger_id: str
    timestamp_utc: datetime
    trading_day: date

    source_event_id: str
    source_event_type: str

    scope: str
    scope_id: Optional[str]

    capital_before: Decimal
    capital_after: Decimal
    capital_delta: Decimal

    reason: str
