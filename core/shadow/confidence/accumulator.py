# core/shadow/confidence/accumulator.py
from core.shadow.confidence.models import (
    ShadowConfidenceState,
    ShadowConfidenceSnapshot,
)


class ShadowConfidenceAccumulator:
    """
    Accumulates confidence over time from shadow-vs-live divergence.

    Divergence score convention:
    - 0.0   → perfect match
    - 1.0+  → severe mismatch
    """

    def __init__(
        self,
        *,
        gain_rate: float = 0.02,
        decay_rate: float = 0.05,
        acceptable_divergence: float = 0.2,
    ):
        self.gain_rate = gain_rate
        self.decay_rate = decay_rate
        self.acceptable_divergence = acceptable_divergence

    def update(
        self,
        state: ShadowConfidenceState,
        *,
        divergence_score: float,
    ) -> ShadowConfidenceSnapshot:
        """
        Update confidence based on a new divergence observation.
        """

        confidence = state.confidence
        obs = state.observations + 1

        # Normalize effect by experience
        inertia = min(1.0, obs / 20.0)

        if divergence_score <= self.acceptable_divergence:
            # Reward consistency slowly
            confidence += self.gain_rate * (1.0 - inertia)
        else:
            # Penalize divergence aggressively
            confidence -= self.decay_rate * inertia

        # Clamp
        confidence = max(0.0, min(1.0, confidence))

        # Update state
        state.confidence = confidence
        state.observations = obs

        return ShadowConfidenceSnapshot(
            strategy_id=state.strategy_id,
            confidence=round(confidence, 3),
            observations=obs,
            last_divergence_score=divergence_score,
        )
