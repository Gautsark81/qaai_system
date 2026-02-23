# core/strategy_factory/screening/ensemble_intelligence.py

from __future__ import annotations

from decimal import Decimal
from typing import Dict

from .screening_models import ScreeningResult
from .ensemble_models import (
    EnsembleSignal,
    EnsembleIntelligenceReport,
)
from .ensemble_hash import compute_ensemble_state_hash


class StrategyEnsembleIntelligence:
    """
    C5.6 — Advisory Ensemble Intelligence Layer

    HARD RULES:
    - Deterministic
    - Advisory only
    - No mutation
    - No selection
    - No capital authority
    - No lifecycle authority
    """

    def analyze(
        self,
        *,
        screening_result: ScreeningResult,
        ssr_map: Dict[str, Decimal] | None = None,
    ) -> EnsembleIntelligenceReport:

        scores = screening_result.scores

        if not scores:
            signals = ()
            return EnsembleIntelligenceReport(
                signals=signals,
                state_hash=compute_ensemble_state_hash(signals),
            )

        # ---------------------------------------------------
        # 1️⃣ Concentration Signal
        # ---------------------------------------------------
        total_score = sum(Decimal(s.score) for s in scores)
        top_score = Decimal(scores[0].score)

        concentration = (
            (top_score / total_score)
            if total_score > 0
            else Decimal("0")
        )

        concentration_signal = EnsembleSignal(
            signal_type="TOP_SCORE_CONCENTRATION",
            value=concentration.quantize(Decimal("0.0001")),
            description="Share of total score held by top strategy",
        )

        # ---------------------------------------------------
        # 2️⃣ Diversity Signal
        # ---------------------------------------------------
        unique_count = Decimal(len(scores))

        diversity_signal = EnsembleSignal(
            signal_type="STRATEGY_COUNT",
            value=unique_count,
            description="Number of screened strategies",
        )

        # ---------------------------------------------------
        # 3️⃣ SSR Strength Signal (optional)
        # ---------------------------------------------------
        ssr_strength = Decimal("0")

        if ssr_map:
            valid = [
                ssr_map.get(s.strategy_dna, Decimal("0"))
                for s in scores
            ]
            if valid:
                ssr_strength = sum(valid) / Decimal(len(valid))

        ssr_signal = EnsembleSignal(
            signal_type="AVERAGE_SSR",
            value=ssr_strength.quantize(Decimal("0.0001")),
            description="Average SSR of screened strategies",
        )

        signals = (
            concentration_signal,
            diversity_signal,
            ssr_signal,
        )

        return EnsembleIntelligenceReport(
            signals=signals,
            state_hash=compute_ensemble_state_hash(signals),
        )