from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Dict

from core.strategy_factory.health.resurrection.enums import OutcomeState


# ======================================================
# Learning Signal (PURE VALUE OBJECT)
# ======================================================

@dataclass(frozen=True)
class ResurrectionLearningSignal:
    """
    Deterministic learning output for resurrection governance.
    """

    allowed: bool
    failure_count: int
    cooldown_until: Optional[datetime]
    reason: str


# ======================================================
# Resurrection Outcome Artifact (READ-ONLY CONTRACT)
# ======================================================

@dataclass(frozen=True)
class ResurrectionOutcomeArtifact:
    """
    Immutable record describing the outcome of a resurrection attempt.

    NOTE:
    - `outcome` is DERIVED if not provided
    - Backward compatible with tests that only pass `success`
    """

    dna: str
    success: bool
    timestamp: datetime
    outcome: Optional[OutcomeState] = None
    notes: Optional[str] = None

    def __post_init__(self):
        if self.outcome is None:
            derived = (
                OutcomeState.SUCCESS
                if self.success
                else OutcomeState.FAILURE
            )
            object.__setattr__(self, "outcome", derived)


# ======================================================
# Resurrection Learning Engine (PURE LOGIC)
# ======================================================

class ResurrectionLearningEngine:
    """
    Stateless, deterministic learning evaluator.
    """

    MAX_FAILURES: int = 2
    COOLDOWN_DAYS: int = 30

    @classmethod
    def evaluate(
        cls,
        *,
        strategy_dna: str,
        outcomes: Iterable[ResurrectionOutcomeArtifact],
        now: Optional[datetime] = None,
    ) -> ResurrectionLearningSignal:
        now = now or datetime.utcnow()

        relevant = [o for o in outcomes if o.dna == strategy_dna]
        failures = [o for o in relevant if not o.success]
        failure_count = len(failures)

        if failure_count >= cls.MAX_FAILURES:
            last_failure = max(failures, key=lambda o: o.timestamp)
            cooldown_until = last_failure.timestamp + timedelta(
                days=cls.COOLDOWN_DAYS
            )

            if now < cooldown_until:
                return ResurrectionLearningSignal(
                    allowed=False,
                    failure_count=failure_count,
                    cooldown_until=cooldown_until,
                    reason=(
                        f"Resurrection blocked: {failure_count} failures, "
                        f"cooldown active until {cooldown_until.isoformat()}"
                    ),
                )

        return ResurrectionLearningSignal(
            allowed=True,
            failure_count=failure_count,
            cooldown_until=None,
            reason="Resurrection allowed by learning engine",
        )


# ======================================================
# Resurrection Learning Store (STATEFUL, DETERMINISTIC)
# ======================================================

class ResurrectionLearningStore:
    """
    Append-only, deterministic learning store.
    """

    def __init__(self):
        self._outcomes: Dict[str, List[ResurrectionOutcomeArtifact]] = {}

    # -------------------------------
    # Write API
    # -------------------------------

    def record_outcome(
        self,
        dna: str,
        outcome: OutcomeState,
        timestamp: datetime,
        notes: Optional[str] = None,
    ) -> None:
        artifact = ResurrectionOutcomeArtifact(
            dna=dna,
            success=(outcome == OutcomeState.SUCCESS),
            outcome=outcome,
            timestamp=timestamp,
            notes=notes,
        )

        self._outcomes.setdefault(dna, []).append(artifact)
        self._outcomes[dna].sort(key=lambda o: o.timestamp)

    # -------------------------------
    # Read API
    # -------------------------------

    def history(self, dna: str) -> List[ResurrectionOutcomeArtifact]:
        return list(self._outcomes.get(dna, []))

    def evaluate(
        self,
        dna: str,
        *,
        now: Optional[datetime] = None,
    ) -> ResurrectionLearningSignal:
        return ResurrectionLearningEngine.evaluate(
            strategy_dna=dna,
            outcomes=self.history(dna),
            now=now,
        )
