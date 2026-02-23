# core/strategy_factory/capital/throttling.py

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

from core.strategy_factory.capital.throttling_models import (
    CapitalThrottleDecision,
)

# NEW: regime integration (safe import boundary)
try:
    from core.strategy_factory.capital.regime_integration import (
        RegimeCapitalContext,
    )
except Exception:  # defensive for legacy environments
    RegimeCapitalContext = None  # type: ignore


__all__ = [
    "CapitalThrottleDecision",
    "ThrottleAuditEvent",
    "ThrottleAuditLedger",
    "decide_capital_throttle",
    "evaluate_capital_throttle",
    "get_throttle_audit_ledger",
]


# ==========================================================
# Audit Event Model (IMMUTABLE)
# ==========================================================


@dataclass(frozen=True)
class ThrottleAuditEvent:
    strategy_dna: str
    requested_capital: float
    effective_requested_capital: float  # NEW (non-breaking addition)
    allowed: bool
    was_throttled: bool
    retry_after_seconds: Optional[int]
    evaluated_at: datetime

    # C4.6 Phase 2 — governance extension (non-breaking)
    governance_chain_id: Optional[str] = None

    # C16 — regime integration extension (non-breaking)
    regime_multiplier: Optional[float] = None
    regime_freeze: Optional[bool] = None


# ==========================================================
# Append-Only Ledger
# ==========================================================


class ThrottleAuditLedger:

    def __init__(self) -> None:
        self._events: List[ThrottleAuditEvent] = []

    def append(self, event: ThrottleAuditEvent) -> None:
        if not isinstance(event, ThrottleAuditEvent):
            raise TypeError("event must be ThrottleAuditEvent")
        self._events.append(event)

    @property
    def events(self) -> List[ThrottleAuditEvent]:
        return list(self._events)

    def snapshot_state(self) -> List[dict]:
        return [
            {
                "strategy_dna": e.strategy_dna,
                "requested_capital": e.requested_capital,
                "effective_requested_capital": e.effective_requested_capital,
                "allowed": e.allowed,
                "was_throttled": e.was_throttled,
                "retry_after_seconds": e.retry_after_seconds,
                "evaluated_at": e.evaluated_at.isoformat(),
                "governance_chain_id": e.governance_chain_id,
                "regime_multiplier": e.regime_multiplier,
                "regime_freeze": e.regime_freeze,
            }
            for e in self._events
        ]

    def _reset(self) -> None:
        self._events.clear()


_THROTTLE_LEDGER = ThrottleAuditLedger()


def get_throttle_audit_ledger() -> ThrottleAuditLedger:
    return _THROTTLE_LEDGER


# ==========================================================
# PURE THROTTLING LOGIC (UNCHANGED)
# ==========================================================


def decide_capital_throttle(
    *,
    last_allocation_at: Optional[datetime],
    cooldown_seconds: int,
    now: datetime,
) -> CapitalThrottleDecision:

    if cooldown_seconds < 0:
        raise ValueError("cooldown_seconds must be >= 0")

    if last_allocation_at is None:
        return CapitalThrottleDecision(
            allowed=True,
            reason="Throttle allowed (no prior allocation)",
            retry_after_seconds=None,
        )

    elapsed = int((now - last_allocation_at).total_seconds())

    if elapsed >= cooldown_seconds:
        return CapitalThrottleDecision(
            allowed=True,
            reason="Throttle allowed (cooldown elapsed)",
            retry_after_seconds=None,
        )

    remaining = cooldown_seconds - elapsed

    return CapitalThrottleDecision(
        allowed=False,
        reason="Throttle blocked (cooldown active)",
        retry_after_seconds=remaining,
    )


# ==========================================================
# ENGINE-FACING HOOK (C16 Integrated)
# ==========================================================


def evaluate_capital_throttle(
    *,
    strategy_dna: str,
    requested_capital: float,
    last_allocation_at: Optional[datetime],
    cooldown_seconds: int,
    now: datetime,
    governance_chain_id: Optional[str] = None,
    regime_context: Optional["RegimeCapitalContext"] = None,  # NEW
) -> CapitalThrottleDecision:

    # Governance enforcement rule:
    if governance_chain_id is not None and not governance_chain_id:
        raise ValueError("governance_chain_id cannot be empty")

    # ------------------------------------------------------
    # C16 — Regime Pre-Processing (Advisory Only)
    # ------------------------------------------------------

    effective_requested_capital = requested_capital
    regime_multiplier = None
    regime_freeze = None

    if regime_context is not None:
        regime_multiplier = regime_context.multiplier
        regime_freeze = regime_context.freeze_new_allocations

        # Freeze takes full precedence
        if regime_context.freeze_new_allocations:
            effective_requested_capital = 0.0
        else:
            effective_requested_capital = round(
                requested_capital * regime_context.multiplier, 6
            )

    # ------------------------------------------------------
    # Cooldown Throttle (UNCHANGED LOGIC)
    # ------------------------------------------------------

    decision = decide_capital_throttle(
        last_allocation_at=last_allocation_at,
        cooldown_seconds=cooldown_seconds,
        now=now,
    )

    # ------------------------------------------------------
    # Audit Event (Append-Only)
    # ------------------------------------------------------

    event = ThrottleAuditEvent(
        strategy_dna=strategy_dna,
        requested_capital=requested_capital,
        effective_requested_capital=effective_requested_capital,
        allowed=decision.allowed,
        was_throttled=not decision.allowed,
        retry_after_seconds=decision.retry_after_seconds,
        evaluated_at=now,
        governance_chain_id=governance_chain_id,
        regime_multiplier=regime_multiplier,
        regime_freeze=regime_freeze,
    )

    _THROTTLE_LEDGER.append(event)

    return decision