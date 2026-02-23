from domain.strategy_lifecycle.lifecycle_state import StrategyLifecycleState
from domain.strategy_lifecycle.health_classifier import StrategyHealthClassifier
from domain.strategy_lifecycle.health_snapshot import StrategyHealthSnapshot


class LifecycleAdvisor:
    """
    Suggests lifecycle changes based on health.
    """

    @staticmethod
    def suggest(
        current: StrategyLifecycleState,
        snapshot: StrategyHealthSnapshot,
    ) -> StrategyLifecycleState:
        healthy = StrategyHealthClassifier.is_healthy(snapshot)

        if not healthy and current == StrategyLifecycleState.LIVE:
            return StrategyLifecycleState.DEGRADED

        return current
