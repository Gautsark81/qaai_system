# core/strategy_factory/capital/promotion_gate.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from core.strategy_factory.capital.throttling import (
    get_throttle_audit_ledger,
)
from core.strategy_factory.capital.throttling import ThrottleAuditEvent


__all__ = [
    "PromotionGateResult",
    "evaluate_strategy_promotion",
]


# ==========================================================
# Promotion Result Model
# ==========================================================


@dataclass(frozen=True)
class PromotionGateResult:
    allowed: bool
    discipline_score: float
    total_events: int
    throttle_events: int
    message: str


# ==========================================================
# Governance Constants
# ==========================================================

MIN_DISCIPLINE_SCORE = 0.80
MAX_ALLOWED_THROTTLE_RATIO = 0.40


# ==========================================================
# Core Evaluation Logic (PURE, DETERMINISTIC)
# ==========================================================


def evaluate_strategy_promotion(
    *,
    strategy_dna: str,
    min_discipline_score: float = MIN_DISCIPLINE_SCORE,
    max_throttle_ratio: float = MAX_ALLOWED_THROTTLE_RATIO,
) -> PromotionGateResult:
    """
    Evaluate whether a strategy is eligible for promotion
    based on capital discipline history.

    Deterministic:
    - Reads append-only throttle ledger
    - No wall-clock access
    - No mutation
    """

    ledger = get_throttle_audit_ledger()
    events: List[ThrottleAuditEvent] = ledger.events

    strategy_events = [e for e in events if e.strategy_dna == strategy_dna]

    total_events = len(strategy_events)

    if total_events == 0:
        # No capital behavior yet — fail safe
        return PromotionGateResult(
            allowed=False,
            discipline_score=0.0,
            total_events=0,
            throttle_events=0,
            message="Promotion denied (no capital history)",
        )

    throttle_events = sum(1 for e in strategy_events if e.was_throttled)

    throttle_ratio = throttle_events / total_events

    discipline_score = 1.0 - throttle_ratio

    # Hard Governance Rules
    if discipline_score < min_discipline_score:
        return PromotionGateResult(
            allowed=False,
            discipline_score=discipline_score,
            total_events=total_events,
            throttle_events=throttle_events,
            message="Promotion denied (discipline score below threshold)",
        )

    if throttle_ratio > max_throttle_ratio:
        return PromotionGateResult(
            allowed=False,
            discipline_score=discipline_score,
            total_events=total_events,
            throttle_events=throttle_events,
            message="Promotion denied (excessive throttling behavior)",
        )

    return PromotionGateResult(
        allowed=True,
        discipline_score=discipline_score,
        total_events=total_events,
        throttle_events=throttle_events,
        message="Promotion approved (capital discipline satisfied)",
    )