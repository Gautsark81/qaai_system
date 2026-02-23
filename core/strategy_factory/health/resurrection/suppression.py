from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.strategy_factory.health.resurrection.enums import (
    OutcomeState,
    SuppressionState,
)


class ResurrectionSuppressionEngine:
    """
    Deterministic suppression engine that prevents repeated
    failed strategies from being resurrected too aggressively.
    """

    def __init__(
        self,
        *,
        failure_threshold: int,
        cooldown_period: timedelta,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._cooldown_period = cooldown_period
        self._outcomes: Dict[str, List[datetime]] = {}

    def record_outcome(
        self,
        dna: str,
        outcome: OutcomeState,
        *,
        timestamp: Optional[datetime] = None,
    ) -> None:
        if outcome != OutcomeState.FAILURE:
            return

        ts = timestamp or datetime.utcnow()
        self._outcomes.setdefault(dna, []).append(ts)

    def state(self, dna: str) -> SuppressionState:
        failures = self._outcomes.get(dna, [])
        if len(failures) >= self._failure_threshold:
            return SuppressionState.SUPPRESSED
        return SuppressionState.ALLOWED

    def is_allowed(
        self,
        dna: str,
        *,
        at_time: datetime,
    ) -> bool:
        failures = self._outcomes.get(dna, [])
        if len(failures) < self._failure_threshold:
            return True

        last_failure = failures[-1]
        return at_time >= last_failure + self._cooldown_period
