from __future__ import annotations

from typing import Set

from core.strategy_factory.health.decay.model import DecaySnapshot
from core.strategy_factory.registry import StrategyRecord


class ResurrectionPolicy:
    """
    Determines whether a strategy is eligible for resurrection.

    Resurrection is a SHADOW / EVALUATION process, not execution.
    Execution safety is enforced separately by ExecutionGuard.
    """

    # States that are allowed to enter resurrection evaluation
    ELIGIBLE_STATES: Set[str] = {
        "GENERATED",      # registry entry point (authoritative)
        "RETIRED",
        "INACTIVE",
        "FAILED",
        "ARCHIVED",
        "EXPERIMENTAL",
    }


    # States that must NEVER be resurrected
    BLOCKED_STATES: Set[str] = {
        "LIVE",
        "ACTIVE",
        "PAPER_TRADING",
        "RESURRECTION_CANDIDATE",
        "REVIVAL_SHADOW",
    }

    @staticmethod
    def is_eligible(
        record: StrategyRecord,
        decay: DecaySnapshot,
    ) -> bool:
        # Absolute safety block
        if record.state in ResurrectionPolicy.BLOCKED_STATES:
            return False

        # Must be non-live lifecycle state
        if record.state not in ResurrectionPolicy.ELIGIBLE_STATES:
            return False

        # Decay must indicate recovery potential
        if decay.decay_score < 0.5:
            return False

        # Strategy must have had positive historical edge
        if decay.historical_edge <= 0:
            return False

        # Regime change must justify re-evaluation
        if not decay.regime_shift_detected:
            return False

        return True

    @staticmethod
    def reason(decay: DecaySnapshot) -> str:
        return (
            f"Resurrection triggered: decay_score={decay.decay_score:.2f}, "
            f"historical_edge={decay.historical_edge:.2f}, "
            f"regime={decay.regime}, "
            f"regime_shift_detected={decay.regime_shift_detected}"
        )
