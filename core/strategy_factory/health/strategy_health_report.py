from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class StrategyHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DYING = "DYING"
    DEAD = "DEAD"


@dataclass(frozen=True)
class StrategyHealthReport:
    """
    Governance-grade, advisory-only strategy health report.

    Properties:
    - Deterministic
    - Side-effect free
    - Advisory only (never executes, never enforces)
    - Safe for dashboards, audits, and promotion gates
    """

    strategy_id: str
    recent_returns: List[float]
    win_rate: float
    drawdown: float
    trade_count: int
    last_active_at: Optional[datetime]

    advisory_only: bool = field(init=False, default=True)
    status: StrategyHealthStatus = field(init=False)
    health_score: int = field(init=False)
    reasons: List[str] = field(init=False)

    # ----------------------------
    # Lifecycle
    # ----------------------------

    def __post_init__(self):
        object.__setattr__(self, "reasons", [])
        self._validate_inputs()
        self._evaluate_health()

    # ----------------------------
    # Validation
    # ----------------------------

    def _validate_inputs(self) -> None:
        if self.last_active_at is not None and self.last_active_at.tzinfo is None:
            raise ValueError("last_active_at must be timezone-aware (UTC)")

    # ----------------------------
    # Core Evaluation Logic
    # ----------------------------

    def _evaluate_health(self) -> None:
        # HARD TERMINAL CONDITION
        if self.trade_count == 0:
            self._mark_dead("No trades executed")
            return

        inactive = self._is_inactive(days=30)

        score = 100

        # Win rate
        if self.win_rate < 0.4:
            score -= 30
            self.reasons.append("Low win rate")
        elif self.win_rate < 0.55:
            score -= 15
            self.reasons.append("Moderate win rate")

        # Drawdown
        if self.drawdown <= -20:
            score -= 40
            self.reasons.append("Severe drawdown")
        elif self.drawdown <= -10:
            score -= 20
            self.reasons.append("Elevated drawdown")

        # Inactivity penalty (still affects score)
        if inactive:
            score -= 30
            self.reasons.append("Strategy inactive")

        score = max(score, 0)

        # ----------------------------
        # STATUS DERIVATION (GOVERNANCE FIRST)
        # ----------------------------

        if inactive:
            status = StrategyHealthStatus.DYING
        else:
            status = self._derive_status_from_score(score)

        object.__setattr__(self, "health_score", score)
        object.__setattr__(self, "status", status)

        if not self.reasons:
            self.reasons.append("Strategy operating within healthy parameters")

    # ----------------------------
    # Helpers
    # ----------------------------

    def _is_inactive(self, *, days: int) -> bool:
        if self.last_active_at is None:
            return True

        now = datetime.now(timezone.utc)
        return (now - self.last_active_at).days >= days

    def _derive_status_from_score(self, score: int) -> StrategyHealthStatus:
        if score >= 75:
            return StrategyHealthStatus.HEALTHY
        if score >= 50:
            return StrategyHealthStatus.DEGRADED
        if score > 0:
            return StrategyHealthStatus.DYING
        return StrategyHealthStatus.DEAD

    def _mark_dead(self, reason: str) -> None:
        object.__setattr__(self, "health_score", 0)
        object.__setattr__(self, "status", StrategyHealthStatus.DEAD)
        self.reasons.append(reason)
