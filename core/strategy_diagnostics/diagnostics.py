from .health_metrics import StrategyHealthMetrics
from .health_score import StrategyHealthScore


class StrategyDiagnosticsEngine:
    """
    Deterministic strategy diagnostics engine.

    Computes advisory health scores.
    """

    @staticmethod
    def evaluate(metrics: StrategyHealthMetrics) -> StrategyHealthScore:
        if metrics.drawdown > 0.3:
            return StrategyHealthScore(score=0.2, status="CRITICAL")

        if metrics.win_rate < 0.4:
            return StrategyHealthScore(score=0.4, status="WEAK")

        if metrics.pnl > 0 and metrics.win_rate > 0.55:
            return StrategyHealthScore(score=0.8, status="HEALTHY")

        return StrategyHealthScore(score=0.6, status="NEUTRAL")
