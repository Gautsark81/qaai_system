from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from .screening_models import ScreeningScore, ScreeningResult
from .screening_hash import compute_screening_state_hash


class RegimeScoringOverlay:
    """
    C5.2 — Regime-Aware Screening Overlay

    HARD RULES:
    - Deterministic
    - No authority
    - No lifecycle mutation
    - No capital mutation
    - No promotion logic
    - Backward compatible
    """

    def apply(
        self,
        base_result: ScreeningResult,
        regime: Optional[str] = None,
        regime_weights: Optional[Dict[str, Decimal]] = None,
    ) -> ScreeningResult:
        """
        Supported call styles:

        1) apply(result, weights)
        2) apply(result, regime, weights)
        3) apply(result, regime="BULL", regime_weights={...})

        `regime` is informational only.
        """

        # -------------------------------------------------
        # Backward compatibility handling
        # -------------------------------------------------

        # Case: apply(result, weights)
        if regime_weights is None and isinstance(regime, dict):
            weights = regime
        else:
            weights = regime_weights or {}

        if not isinstance(weights, dict):
            raise TypeError("regime_weights must be dict[str, Decimal]")

        adjusted_scores = []

        # -------------------------------------------------
        # Deterministic adjustment
        # -------------------------------------------------
        for s in base_result.scores:
            multiplier = weights.get(
                s.strategy_dna,
                Decimal("1.0"),
            )

            adjusted_value = Decimal(s.score) * Decimal(multiplier)

            adjusted_scores.append(
                ScreeningScore(
                    strategy_dna=s.strategy_dna,
                    score=adjusted_value,
                    rank=0,
                    metrics_hash=s.metrics_hash,
                )
            )

        # -------------------------------------------------
        # Deterministic ranking
        # -------------------------------------------------
        adjusted_scores = sorted(
            adjusted_scores,
            key=lambda x: (-x.score, x.strategy_dna),
        )

        final_scores = []
        for idx, s in enumerate(adjusted_scores, start=1):
            final_scores.append(
                ScreeningScore(
                    strategy_dna=s.strategy_dna,
                    score=s.score,
                    rank=idx,
                    metrics_hash=s.metrics_hash,
                )
            )

        return ScreeningResult(
            scores=tuple(final_scores),
            state_hash=compute_screening_state_hash(final_scores),
        )


# Backward compatibility alias required by tests
RegimeOverlay = RegimeScoringOverlay