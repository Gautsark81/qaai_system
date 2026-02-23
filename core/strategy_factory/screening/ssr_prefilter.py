# core/strategy_factory/screening/ssr_prefilter.py

from __future__ import annotations

from decimal import Decimal
from typing import Dict

from .screening_models import ScreeningResult, ScreeningScore
from .screening_hash import compute_screening_state_hash


class SSRPreFilter:
    """
    C5.4 — SSR-Aware Screening Pre-Filter

    HARD RULES:
    - Deterministic
    - No authority
    - No lifecycle mutation
    - No capital mutation
    - Pure transformation
    """

    def filter(
        self,
        result: ScreeningResult,
        ssr_map: Dict[str, Decimal],
        threshold: Decimal,
    ) -> ScreeningResult:
        """
        ssr_map:
            dict[dna] -> SSR value

        threshold:
            minimum SSR required
        """

        filtered = []

        for score in result.scores:
            ssr = ssr_map.get(score.strategy_dna, Decimal("0"))
            if ssr >= threshold:
                filtered.append(score)

        # Deterministic re-ranking
        final_scores = []
        for idx, s in enumerate(filtered, start=1):
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