from __future__ import annotations

from typing import Iterable
from datetime import datetime

from core.strategy_factory.health.resurrection.policy import ResurrectionPolicy
from core.strategy_factory.health.resurrection.learning import (
    ResurrectionLearningEngine,
    ResurrectionOutcomeArtifact,
)
from core.strategy_factory.health.decay.model import DecaySnapshot
from core.strategy_factory.registry import StrategyRecord


class ResurrectionPolicyGate:
    """
    Combines static eligibility rules with learned suppression logic.

    RULE ORDER (STRICT):
    1. Static policy eligibility (state + decay)
    2. Learning-based suppression / cooldown

    This class:
    - DOES NOT mutate registry
    - DOES NOT create lifecycle transitions
    - ONLY answers: "May we attempt resurrection?"
    """

    @staticmethod
    def may_attempt_resurrection(
        *,
        record: StrategyRecord,
        decay: DecaySnapshot,
        outcomes: Iterable[ResurrectionOutcomeArtifact],
        now: datetime | None = None,
    ) -> bool:
        """
        Final gate for resurrection attempts.

        Returns
        -------
        bool
            True → resurrection evaluation allowed
            False → blocked by policy or learning
        """

        # ----------------------------------
        # Phase 1 — Static eligibility
        # ----------------------------------
        if not ResurrectionPolicy.is_eligible(record, decay):
            return False

        # ----------------------------------
        # Phase 2 — Learning suppression
        # ----------------------------------
        learning_signal = ResurrectionLearningEngine.evaluate(
            strategy_dna=record.dna,
            outcomes=outcomes,
            now=now,
        )

        return learning_signal.allowed
