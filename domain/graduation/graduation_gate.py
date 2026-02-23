from domain.graduation.strategy_performance_snapshot import (
    StrategyPerformanceSnapshot
)
from domain.graduation.graduation_policy import GraduationPolicy


class GraduationGate:
    """
    Determines if a strategy may graduate.
    """

    @staticmethod
    def allow(
        snapshot: StrategyPerformanceSnapshot,
        policy: GraduationPolicy,
    ) -> bool:

        if snapshot.ssr < policy.min_ssr:
            return False

        if snapshot.live_days < policy.min_live_days:
            return False

        if snapshot.max_drawdown_pct > policy.max_drawdown_pct:
            return False

        if snapshot.total_trades < policy.min_trades:
            return False

        return True
