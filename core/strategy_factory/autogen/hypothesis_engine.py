# core/strategy_factory/autogen/hypothesis_engine.py

from typing import List, Optional
from .hypothesis_models import StrategyHypothesis


MAX_NEW_CANDIDATES_PER_CYCLE = 5
HYPOTHESIS_VERSION = 1


class HypothesisEngine:

    def __init__(self, feedback_engine: Optional[object] = None):
        """
        feedback_engine: Optional RetirementFeedbackEngine
        Must expose:
            get_feature_penalty(feature: str) -> float
        """

        self.feedback_engine = feedback_engine

        self._feature_pool = [
            "momentum",
            "mean_reversion",
            "volatility_breakout",
            "trend_strength",
        ]

        self._timeframes = ["5m", "15m", "1h"]

        self._entry_templates = [
            "cross_above_threshold",
            "cross_below_threshold",
        ]

        self._exit_templates = [
            "fixed_rr",
            "trailing_stop",
        ]

    # --------------------------------------------------
    # Public Generation API
    # --------------------------------------------------
    def generate(self, regime_score: float) -> List[StrategyHypothesis]:
        """
        Deterministic hypothesis generation.
        Regime-aware + feedback-aware.
        Fully replay-safe.
        """

        regime_target = self._classify_regime(regime_score)

        hypotheses: List[StrategyHypothesis] = []

        count = 0

        for feature in self._feature_pool:
            for tf in self._timeframes:
                for entry in self._entry_templates:
                    for exit_rule in self._exit_templates:

                        if count >= MAX_NEW_CANDIDATES_PER_CYCLE:
                            return hypotheses

                        feature_weight = self._regime_weight(
                            feature,
                            regime_target,
                        )

                        hypothesis = StrategyHypothesis(
                            hypothesis_id=self._build_id(
                                feature,
                                tf,
                                entry,
                                exit_rule,
                            ),
                            version=HYPOTHESIS_VERSION,
                            feature_set={feature: feature_weight},
                            entry_logic=entry,
                            exit_logic=exit_rule,
                            timeframe=tf,
                            regime_target=regime_target,
                        )

                        hypotheses.append(hypothesis)
                        count += 1

        return hypotheses

    # --------------------------------------------------
    # Regime Classification
    # --------------------------------------------------
    def _classify_regime(self, regime_score: float) -> str:
        if regime_score > 0.3:
            return "BULL"
        elif regime_score < -0.3:
            return "BEAR"
        else:
            return "NEUTRAL"

    # --------------------------------------------------
    # Feature Weighting (Regime + Feedback)
    # --------------------------------------------------
    def _regime_weight(self, feature: str, regime: str) -> float:
        """
        Deterministic feature weighting.
        Applies:
            1. Regime bias
            2. Retirement feedback penalty (if available)
        """

        # ---- Base regime weight ----
        base_weight = 1.0

        if regime == "BULL" and feature == "momentum":
            base_weight = 1.2
        elif regime == "BEAR" and feature == "mean_reversion":
            base_weight = 1.2

        # ---- Apply retirement feedback penalty ----
        if self.feedback_engine is not None:
            penalty = self.feedback_engine.get_feature_penalty(feature)

            # Penalty bounded and deterministic
            base_weight *= (1 - penalty)

        return round(base_weight, 6)

    # --------------------------------------------------
    # Deterministic ID Builder
    # --------------------------------------------------
    def _build_id(
        self,
        feature: str,
        tf: str,
        entry: str,
        exit_rule: str,
    ) -> str:
        return f"{feature}|{tf}|{entry}|{exit_rule}|v{HYPOTHESIS_VERSION}"