# core/resilience/extreme_events/classifier.py
from typing import Dict
from core.resilience.extreme_events.models import (
    ExtremeEventClassification,
    ExtremeEventType,
)


class ExtremeEventClassifier:
    """
    Classifies extreme conditions deterministically.

    NOTE:
    - No inference
    - No learning
    - Threshold-based only
    """

    def classify(self, *, metrics: Dict[str, float]) -> ExtremeEventClassification:
        """
        metrics expected (if present):
        - market_return
        - volatility
        - liquidity
        - system_error_rate
        """

        # Defaults
        event_type = ExtremeEventType.NORMAL
        severity = 0.0

        if metrics.get("system_error_rate", 0.0) > 0.2:
            event_type = ExtremeEventType.SYSTEM_ANOMALY
            severity = min(1.0, metrics["system_error_rate"])

        elif metrics.get("liquidity", 1.0) < 0.3:
            event_type = ExtremeEventType.LIQUIDITY_FREEZE
            severity = 1.0 - metrics["liquidity"]

        elif metrics.get("market_return", 0.0) < -0.05:
            event_type = ExtremeEventType.MARKET_CRASH
            severity = min(1.0, abs(metrics["market_return"]))

        elif metrics.get("volatility", 0.0) > 0.5:
            event_type = ExtremeEventType.VOLATILITY_SPIKE
            severity = min(1.0, metrics["volatility"])

        return ExtremeEventClassification(
            event_type=event_type,
            severity=round(severity, 3),
            evidence=metrics,
        )
