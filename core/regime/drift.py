from collections import deque
from dataclasses import dataclass
from typing import Deque

from core.regime.taxonomy import MarketRegime


@dataclass(frozen=True)
class RegimeDriftPolicy:
    """
    Policy controlling regime stability detection.
    """
    window: int = 5
    max_changes: int = 2


class RegimeDriftDetector:
    """
    Detects regime instability and transitions over time.

    Uses a sliding window of recent regimes.
    """

    def __init__(self, policy: RegimeDriftPolicy):
        self.policy = policy
        self._history: Deque[MarketRegime] = deque(maxlen=policy.window)

    def update(self, regime: MarketRegime) -> None:
        self._history.append(regime)

    def is_transitioning(self) -> bool:
        """
        Returns True if regime has changed frequently
        within the observation window.
        """
        if len(self._history) < self.policy.window:
            return False

        changes = sum(
            1
            for i in range(1, len(self._history))
            if self._history[i] != self._history[i - 1]
        )

        return changes > self.policy.max_changes

    def is_stable(self) -> bool:
        """
        Returns True if regime is stable.
        """
        return not self.is_transitioning()

    def last_regime(self) -> MarketRegime | None:
        return self._history[-1] if self._history else None
