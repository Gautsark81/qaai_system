from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Iterable, Dict, Any, List

from core.strategy_factory.capital.ledger_models import (
    CapitalLedgerEntry,
    CapitalUsageLedgerEntry,
)


# ============================================================
# INTERNAL NORMALIZATION HELPERS
# ============================================================

def _normalize_datetime(dt: datetime) -> str:
    """
    Convert datetime to canonical ISO string.
    Always UTC-normalized representation.
    """
    if dt.tzinfo is not None:
        dt = dt.astimezone(tz=dt.tzinfo)
    return dt.isoformat()


def _normalize_float(value: float) -> str:
    """
    Quantize float to stable 12-decimal fixed representation.
    Prevents float drift hash instability.
    """
    return f"{float(value):.12f}"


def _canonicalize_ledger_entry(e: CapitalLedgerEntry) -> Dict[str, Any]:
    """
    Convert CapitalLedgerEntry into canonical hashable dict.

    EXCLUDES:
    - entry_id (runtime UUID)
    - fingerprint (already deterministic)

    INCLUDES:
    - economic meaning
    """
    return {
        "strategy_dna": e.strategy_dna,
        "event_type": e.event_type.value,
        "amount": _normalize_float(e.amount),
        "source_event_fingerprint": e.source_event_fingerprint,
        "created_at": _normalize_datetime(e.created_at),
        "notes": e.notes,
    }


def _canonicalize_usage_entry(e: CapitalUsageLedgerEntry) -> Dict[str, Any]:
    """
    Canonicalize CapitalUsageLedgerEntry for hashing.
    Decimal values converted to string for determinism.
    """
    return {
        "ledger_id": e.ledger_id,
        "timestamp_utc": e.timestamp_utc.isoformat(),
        "trading_day": e.trading_day.isoformat(),
        "source_event_id": e.source_event_id,
        "source_event_type": e.source_event_type,
        "scope": e.scope,
        "scope_id": e.scope_id,
        "capital_before": str(e.capital_before),
        "capital_after": str(e.capital_after),
        "capital_delta": str(e.capital_delta),
        "reason": e.reason,
    }


# ============================================================
# PUBLIC HASH FUNCTIONS (C4.7)
# ============================================================

def compute_capital_ledger_state_hash(
    entries: Iterable[CapitalLedgerEntry],
) -> str:
    """
    Deterministic state hash of capital ledger.

    Properties:
    - Order-independent
    - Float-stable
    - UUID-independent
    - Replay-safe
    """
    canonical: List[Dict[str, Any]] = [
        _canonicalize_ledger_entry(e) for e in entries
    ]

    # Deterministic ordering
    canonical_sorted = sorted(
        canonical,
        key=lambda x: json.dumps(x, sort_keys=True),
    )

    payload = json.dumps(canonical_sorted, sort_keys=True)

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_capital_usage_state_hash(
    entries: Iterable[CapitalUsageLedgerEntry],
) -> str:
    """
    Deterministic state hash of capital usage ledger.
    """
    canonical: List[Dict[str, Any]] = [
        _canonicalize_usage_entry(e) for e in entries
    ]

    canonical_sorted = sorted(
        canonical,
        key=lambda x: json.dumps(x, sort_keys=True),
    )

    payload = json.dumps(canonical_sorted, sort_keys=True)

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()