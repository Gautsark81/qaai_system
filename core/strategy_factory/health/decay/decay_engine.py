# core/strategy_factory/health/decay/decay_engine.py

from datetime import datetime
from typing import Dict

from .decay_metrics import DecayMetrics
from .decay_report import AlphaDecayReport
from .decay_state import AlphaDecayState


class AlphaDecayDetector:
    def evaluate(
        self,
        strategy_id: str,
        telemetry: Dict[str, float],
    ) -> AlphaDecayReport:
        """
        telemetry expects normalized signals (0–1):
        - performance_decay
        - stability_decay
        - consistency_decay
        - regime_decay
        """

        metrics = DecayMetrics(
            performance=telemetry.get("performance_decay", 0.0),
            stability=telemetry.get("stability_decay", 0.0),
            consistency=telemetry.get("consistency_decay", 0.0),
            regime=telemetry.get("regime_decay", 0.0),
        )

        score = metrics.composite()
        state = self._classify(score)
        confidence = self._confidence(metrics)

        return AlphaDecayReport(
            strategy_id=strategy_id,
            metrics=metrics,
            score=round(score, 4),
            state=state,
            confidence=round(confidence, 3),
            evaluated_at=datetime.utcnow(),
        )

    @staticmethod
    def _classify(score: float) -> AlphaDecayState:
        if score < 0.30:
            return AlphaDecayState.HEALTHY
        if score < 0.55:
            return AlphaDecayState.WARNING
        if score < 0.75:
            return AlphaDecayState.DEGRADING
        return AlphaDecayState.CRITICAL

    @staticmethod
    def _confidence(metrics: DecayMetrics) -> float:
        # Confidence ↓ when signals disagree
        values = [
            metrics.performance,
            metrics.stability,
            metrics.consistency,
            metrics.regime,
        ]
        spread = max(values) - min(values)
        return max(0.2, 1.0 - spread)
