from dataclasses import dataclass

from .snapshot import EnsembleSnapshot


@dataclass(frozen=True)
class StableRegime:
    stable_regime_score: float
    snapshot_hash: str


class RegimeStabilityEngine:

    @staticmethod
    def stabilize(snapshot: EnsembleSnapshot) -> StableRegime:

        prev = snapshot.previous_regime_score
        curr = snapshot.regime_score

        # Limit regime change per cycle
        delta = curr - prev
        max_step = snapshot.regime_max_step

        if delta > max_step:
            delta = max_step
        elif delta < -max_step:
            delta = -max_step

        stepped_regime = prev + delta

        # Exponential smoothing
        alpha = snapshot.regime_smoothing_alpha

        stable_regime = alpha * stepped_regime + (1 - alpha) * prev

        # Clamp to bounds
        stable_regime = max(-1.0, min(1.0, stable_regime))

        return StableRegime(
            stable_regime_score=stable_regime,
            snapshot_hash=snapshot.snapshot_hash,
        )