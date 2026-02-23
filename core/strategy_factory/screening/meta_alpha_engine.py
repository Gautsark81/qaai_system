# core/strategy_factory/screening/meta_alpha_engine.py

from __future__ import annotations

from decimal import Decimal
from typing import Dict

from .screening_models import ScreeningResult
from .ensemble_models import EnsembleIntelligenceReport
from .meta_alpha_models import (
    MetaAlphaSignal,
    MetaAlphaReport,
)
from .meta_alpha_hash import compute_meta_alpha_hash


class MetaAlphaIntelligence:
    """
    C5.7 — Meta-Alpha Advisory Layer

    HARD RULES:
    - Deterministic
    - Advisory only
    - No lifecycle mutation
    - No capital mutation
    - No promotion logic
    - No registry mutation
    """

    def analyze(
        self,
        *,
        screening_result: ScreeningResult,
        ensemble_report: EnsembleIntelligenceReport,
        regime: str | None = None,
    ) -> MetaAlphaReport:

        scores = screening_result.scores

        if not scores:
            signals = ()
            return MetaAlphaReport(
                signals=signals,
                state_hash=compute_meta_alpha_hash(signals),
            )

        # ---------------------------------------------------
        # 1️⃣ Alpha Breadth
        # ---------------------------------------------------
        breadth = Decimal(len(scores))

        breadth_signal = MetaAlphaSignal(
            signal_type="ALPHA_BREADTH",
            value=breadth,
            description="Number of viable alpha candidates",
        )

        # ---------------------------------------------------
        # 2️⃣ Alpha Skew
        # ---------------------------------------------------
        total = sum(Decimal(s.score) for s in scores)
        top = Decimal(scores[0].score)

        skew = (
            (top / total)
            if total > 0
            else Decimal("0")
        )

        skew_signal = MetaAlphaSignal(
            signal_type="ALPHA_SKEW",
            value=skew.quantize(Decimal("0.0001")),
            description="Dominance of top alpha",
        )

        # ---------------------------------------------------
        # 3️⃣ Ensemble Health Projection
        # ---------------------------------------------------
        concentration = next(
            (
                s.value
                for s in ensemble_report.signals
                if s.signal_type == "TOP_SCORE_CONCENTRATION"
            ),
            Decimal("0"),
        )

        fragility = concentration.quantize(Decimal("0.0001"))

        fragility_signal = MetaAlphaSignal(
            signal_type="ALPHA_FRAGILITY",
            value=fragility,
            description="Fragility proxy from ensemble concentration",
        )

        signals = (
            breadth_signal,
            skew_signal,
            fragility_signal,
        )

        return MetaAlphaReport(
            signals=signals,
            state_hash=compute_meta_alpha_hash(signals),
        )