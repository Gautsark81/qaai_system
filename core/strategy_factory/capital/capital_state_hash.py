from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Iterable

from core.strategy_factory.capital.ledger_models import CapitalLedgerEntry


# ============================================================
# C4.7 — Deterministic Capital State Hash
# ============================================================

def _normalize_float(value: float) -> str:
    """
    Normalize float to deterministic string.
    Prevent float drift across platforms.
    """
    return format(Decimal(str(value)), "f")


def _entry_payload(entry: CapitalLedgerEntry) -> dict:
    """
    Canonical representation of a ledger entry for hashing.
    """
    return {
        "strategy_dna": entry.strategy_dna,
        "event_type": entry.event_type.value,
        "amount": _normalize_float(entry.amount),
        "fingerprint": entry.fingerprint,
    }


def compute_capital_state_hash(
    ledger: Iterable[CapitalLedgerEntry],
) -> str:
    """
    Deterministic hash of capital ledger state.

    Guarantees:
    - Order independence
    - Float stability
    - Replay stability
    """

    entries = list(ledger)

    normalized = sorted(
        (_entry_payload(e) for e in entries),
        key=lambda x: (
            x["strategy_dna"] or "",
            x["event_type"],
            x["amount"],
            x["fingerprint"],
        ),
    )

    serialized = json.dumps(normalized, sort_keys=True)

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()