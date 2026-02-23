from domain.strategy_lifecycle.lifecycle_state import StrategyLifecycleState


class LifecycleRules:
    """
    Defines allowed lifecycle transitions.
    """

    ALLOWED = {
        StrategyLifecycleState.CREATED: {
            StrategyLifecycleState.BACKTEST
        },
        StrategyLifecycleState.BACKTEST: {
            StrategyLifecycleState.PAPER
        },
        StrategyLifecycleState.PAPER: {
            StrategyLifecycleState.LIVE_CANDIDATE,
            StrategyLifecycleState.RETIRED,
        },
        StrategyLifecycleState.LIVE_CANDIDATE: {
            StrategyLifecycleState.LIVE,
            StrategyLifecycleState.RETIRED,
        },
        StrategyLifecycleState.LIVE: {
            StrategyLifecycleState.DEGRADED,
            StrategyLifecycleState.PAUSED,
        },
        StrategyLifecycleState.DEGRADED: {
            StrategyLifecycleState.PAUSED,
            StrategyLifecycleState.RETIRED,
        },
    }

    @staticmethod
    def can_transition(
        from_state: StrategyLifecycleState,
        to_state: StrategyLifecycleState,
    ) -> bool:
        return to_state in LifecycleRules.ALLOWED.get(from_state, set())
