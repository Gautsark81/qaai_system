from typing import Dict

from core.lifecycle.contracts.snapshot import LifecycleState


class LifecycleCapitalModifier:
    """
    Deterministic lifecycle → capital scaling mapper.

    Design constraints:
    - PURE function
    - NO side effects
    - NO observability logic
    - NO risk logic
    - FAILS CLOSED for unknown states
    """

    DEFAULT_MULTIPLIERS: Dict[LifecycleState, float] = {
        LifecycleState.CANDIDATE: 0.25,
        LifecycleState.PAPER: 0.50,
        LifecycleState.LIVE: 1.00,
    }

    @classmethod
    def multiplier_for(
        cls,
        *,
        lifecycle_state: LifecycleState,
    ) -> float:
        """
        Return capital multiplier for lifecycle state.

        Unknown or unsupported states return 0.0.
        """
        return cls.DEFAULT_MULTIPLIERS.get(lifecycle_state, 0.0)
