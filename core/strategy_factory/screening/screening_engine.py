# core/strategy_factory/screening/screening_engine.py

from __future__ import annotations

from decimal import Decimal
from typing import Dict, Iterable

from .screening_models import ScreeningScore, ScreeningResult
from .screening_hash import compute_screening_state_hash


class ScreeningEngine:
    """
    C5.1 — Deterministic Alpha Screening Layer

    HARD RULES:
    - No lifecycle mutation
    - No capital allocation
    - No promotion authority
    - No execution authority
    - Pure ranking logic
    """

    def screen(
        self,
        strategy_metrics: Dict[str, Decimal],
    ) -> ScreeningResult:
        """
        strategy_metrics:
            dict[strategy_dna -> raw_score]

        Deterministic:
        - Sorted by raw score DESC
        - Tie-break by DNA ASC
        """

        sorted_items = sorted(
            strategy_metrics.items(),
            key=lambda x: (-x[1], x[0]),
        )

        scores = []
        for idx, (dna, raw_score) in enumerate(sorted_items, start=1):
            scores.append(
                ScreeningScore(
                    strategy_dna=dna,
                    score=Decimal(raw_score),
                    rank=idx,
                    metrics_hash=str(hash(raw_score)),
                )
            )

        result = ScreeningResult(
            scores=tuple(scores),
            state_hash=compute_screening_state_hash(scores),
        )

        return result