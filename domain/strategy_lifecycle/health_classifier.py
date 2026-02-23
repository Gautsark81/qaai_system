from domain.strategy_lifecycle.ssr_drift_detector import SSRDriftDetector
from domain.strategy_lifecycle.health_snapshot import StrategyHealthSnapshot


class StrategyHealthClassifier:
    """
    Classifies strategy health.
    """

    @staticmethod
    def is_healthy(snapshot: StrategyHealthSnapshot) -> bool:
        if snapshot.anomaly_flag:
            return False

        if SSRDriftDetector.is_degraded(
            snapshot.ssr_current,
            snapshot.ssr_reference,
        ):
            return False

        return True
