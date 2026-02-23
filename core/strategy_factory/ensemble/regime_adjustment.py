from dataclasses import dataclass

from .snapshot import EnsembleSnapshot
from .regime_stability import RegimeStabilityEngine


@dataclass(frozen=True)
class RegimeAdjustedParameters:
    adjusted_decay_strength: float
    adjusted_reinforcement_strength: float
    snapshot_hash: str


class RegimeAdjustmentEngine:

    @staticmethod
    def adjust(snapshot: EnsembleSnapshot) -> RegimeAdjustedParameters:

        # Stabilize regime first (C15.3)
        stable = RegimeStabilityEngine.stabilize(snapshot)
        effective_regime = stable.stable_regime_score

        # Defensive regime increases decay sensitivity
        decay_adjustment = (
            snapshot.decay_penalty_strength
            * (1 + (-effective_regime) * snapshot.regime_decay_multiplier)
        )

        # Expansion regime increases reinforcement
        reinforcement_adjustment = (
            snapshot.reinforcement_strength
            * (1 + effective_regime * snapshot.regime_reinforcement_multiplier)
        )

        # Clamp to 0–1 bounds
        decay_adjustment = max(0.0, min(1.0, decay_adjustment))
        reinforcement_adjustment = max(0.0, min(1.0, reinforcement_adjustment))

        return RegimeAdjustedParameters(
            adjusted_decay_strength=decay_adjustment,
            adjusted_reinforcement_strength=reinforcement_adjustment,
            snapshot_hash=snapshot.snapshot_hash,
        )