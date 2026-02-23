from dataclasses import dataclass
from typing import Dict

from core.regime.taxonomy import MarketRegime


@dataclass(frozen=True)
class AlphaRetirementPolicy:
    """
    Policy for soft alpha retirement.

    An alpha is considered decaying if its regime-aware
    SSR stays below threshold for N consecutive windows.
    """
    min_ssr: float = 0.4
    max_consecutive_failures: int = 3


class AlphaRetirementEngine:
    """
    Detects alpha decay and recommends soft retirement.

    This engine NEVER:
    - deletes strategies
    - changes lifecycle
    - stops execution

    It ONLY emits a boolean signal.
    """

    def __init__(self, policy: AlphaRetirementPolicy):
        self.policy = policy
        self._failures: Dict[str, int] = {}

    def update(
        self,
        *,
        alpha_id: str,
        regime: MarketRegime,
        regime_ssr: float,
    ) -> None:
        """
        Update retirement state for an alpha.
        """

        if regime_ssr >= self.policy.min_ssr:
            self._failures[alpha_id] = 0
            return

        self._failures[alpha_id] = self._failures.get(alpha_id, 0) + 1

    def should_retire(self, alpha_id: str) -> bool:
        """
        Returns True if alpha should be softly retired.
        """
        return (
            self._failures.get(alpha_id, 0)
            >= self.policy.max_consecutive_failures
        )

    def failure_count(self, alpha_id: str) -> int:
        return self._failures.get(alpha_id, 0)
