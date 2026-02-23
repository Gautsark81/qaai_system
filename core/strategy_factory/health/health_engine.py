# core/strategy_factory/health/health_engine.py

from datetime import datetime
from typing import List, Optional

from .snapshot import StrategyHealthSnapshot
from .metrics import weighted_score, bounded
from .artifacts import HealthReport

from core.strategy_factory.health.death_reason import DeathReason
from core.strategy_factory.health.death_attribution import DeathAttribution
from core.strategy_factory.health.learning.learning_registry import LearningRegistry
from core.strategy_factory.health.learning.health_learning_context import (
    HealthLearningContext,
)

WEIGHTS = {
    "returns": 0.35,
    "drawdown": 0.20,
    "stability": 0.20,
    "regime": 0.15,
    "complexity": 0.10,
}


class StrategyHealthEngine:
    def evaluate(
        self,
        *,
        strategy_dna: str,
        performance_metrics: dict,
        risk_metrics: dict,
        signal_metrics: dict,
        regime_alignment: dict,
        complexity_penalty: float,
        learning_registry: Optional[LearningRegistry] = None,
    ) -> HealthReport:
        """
        Compute strategy health.

        learning_registry is OPTIONAL and advisory-only.
        It does not affect scoring, flags, or lifecycle decisions.
        """

        values = {
            "returns": performance_metrics.get("sharpe", 0.0),
            "drawdown": 1.0 - risk_metrics.get("max_drawdown", 1.0),
            "stability": 1.0 - signal_metrics.get("entropy", 1.0),
            "regime": sum(regime_alignment.values()) / max(len(regime_alignment), 1),
            "complexity": 1.0 - complexity_penalty,
        }

        health_score = weighted_score(WEIGHTS, values)

        decay_risk = bounded(
            risk_metrics.get("volatility", 0.0)
            * signal_metrics.get("entropy", 0.0)
        )

        confidence = bounded(
            1.0 - abs(signal_metrics.get("autocorr", 0.0))
        )

        flags = []
        if health_score < 0.4:
            flags.append("LOW_HEALTH")
        if decay_risk > 0.6:
            flags.append("HIGH_DECAY_RISK")

        snapshot = StrategyHealthSnapshot(
            strategy_dna=strategy_dna,
            timestamp=datetime.utcnow(),
            health_score=health_score,
            confidence=confidence,
            decay_risk=decay_risk,
            performance_metrics=performance_metrics,
            risk_metrics=risk_metrics,
            signal_metrics=signal_metrics,
            regime_alignment=regime_alignment,
            flags=flags,
        )

        snapshot.validate()

        inputs = {
            "performance": performance_metrics,
            "risk": risk_metrics,
            "signal": signal_metrics,
            "regime": regime_alignment,
            "complexity": complexity_penalty,
        }

        # ---- Phase 11.8-C: learning → health wiring (READ-ONLY) ----
        learning_context = None
        if learning_registry is not None:
            learning_context = HealthLearningContext(
                lifecycle_snapshot=learning_registry.latest_snapshot(),
                failure_mode_stats=learning_registry.latest_failure_stats(),
            )

        return HealthReport(
            snapshot=snapshot,
            inputs_hash=HealthReport.compute_inputs_hash(inputs),
            learning_context=learning_context,
        )


class HealthEngine:
    """
    Lifecycle-focused health engine.

    This engine is responsible ONLY for emitting DeathAttribution
    when a strategy must be killed.

    It does NOT:
    - Score health
    - Persist state
    - Resurrect strategies
    """

    def __init__(self, clock):
        self._clock = clock

    def evaluate_and_maybe_kill(
        self,
        *,
        strategy_id: str,
        equity_curve: List[float],
        ssr: float,
    ) -> Optional[DeathAttribution]:

        if not equity_curve:
            return None

        peak = max(equity_curve)
        current = equity_curve[-1]

        if peak <= 0:
            return None

        drawdown = (current - peak) / peak

        # Phase 11.6-B3 rule: drawdown-based kill ONLY
        if drawdown <= -0.10:
            return DeathAttribution(
                strategy_id=strategy_id,
                reason=DeathReason.MAX_DRAWDOWN,
                timestamp=self._clock.now(),
                triggered_by="health_engine",
                metrics={
                    "drawdown": drawdown,
                    "equity_peak": peak,
                    "equity_now": current,
                    "ssr": ssr,
                },
            )

        return None
