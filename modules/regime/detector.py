from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RegimeFeatures:
    """
    Minimal, replayable features for regime detection.
    """
    volatility: float
    trend_strength: float
    drawdown_pct: float


class RegimeDetector:
    """
    Phase 13.4 — Regime Detector

    Stateless, rule-based regime classification.
    """

    @staticmethod
    def detect(features: RegimeFeatures) -> str:
        """
        Returns one of:
        - 'calm_trend'
        - 'volatile_trend'
        - 'choppy'
        - 'panic'
        """

        # Panic: deep drawdown + high volatility
        if features.drawdown_pct >= 0.20 and features.volatility >= 0.04:
            return "panic"

        # Volatile trend: trend exists but volatility elevated
        if features.trend_strength >= 0.5 and features.volatility >= 0.03:
            return "volatile_trend"

        # Calm trend: trend with low volatility
        if features.trend_strength >= 0.5 and features.volatility < 0.03:
            return "calm_trend"

        # Default: choppy / range-bound
        return "choppy"
