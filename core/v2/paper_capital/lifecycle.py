from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class LifecycleState(str, Enum):
    RESEARCH = "research"
    PAPER_ELIGIBLE = "paper_eligible"
    PAPER_ACTIVE = "paper_active"
    DECAYING = "decaying"
    RETIRED = "retired"


@dataclass(frozen=True)
class ShadowPnLSnapshot:
    step: int
    pnl: int


@dataclass
class StrategyLifecycle:
    """
    Tracks shadow performance and lifecycle state for a strategy.
    """
    strategy_id: str
    state: LifecycleState = LifecycleState.RESEARCH
    pnl_history: List[ShadowPnLSnapshot] = field(default_factory=list)

    # thresholds (governance-tunable)
    decay_threshold: int = -3
    retire_threshold: int = -6

    def record_outcomes(self, outcomes: List[bool]) -> None:
        """
        Update shadow PnL and lifecycle state from outcomes.
        """
        pnl = self.pnl_history[-1].pnl if self.pnl_history else 0
        step = self.pnl_history[-1].step + 1 if self.pnl_history else 1

        for o in outcomes:
            pnl += 1 if o else -1

        self.pnl_history.append(
            ShadowPnLSnapshot(step=step, pnl=pnl)
        )

        self._update_state(pnl)

    # ------------------------------------------------------------------

    def _update_state(self, pnl: int) -> None:
        # Terminal condition
        if pnl <= self.retire_threshold:
            self.state = LifecycleState.RETIRED
            return

        # Decay condition
        if pnl <= self.decay_threshold:
            self.state = LifecycleState.DECAYING
            return

        # Healthy zone
        if self.state in {
            LifecycleState.RESEARCH,
            LifecycleState.PAPER_ELIGIBLE,
            LifecycleState.DECAYING,
        }:
            self.state = LifecycleState.PAPER_ACTIVE
