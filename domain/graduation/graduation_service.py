from domain.graduation.graduation_gate import GraduationGate
from domain.graduation.graduation_level import GraduationLevel
from domain.graduation.strategy_performance_snapshot import (
    StrategyPerformanceSnapshot
)
from domain.graduation.graduation_policy import GraduationPolicy


class GraduationService:
    """
    Governs strategy graduation.
    """

    @staticmethod
    def evaluate(
        snapshot: StrategyPerformanceSnapshot,
        policy: GraduationPolicy,
    ) -> GraduationLevel:

        if GraduationGate.allow(snapshot, policy):
            return GraduationLevel.PRODUCTION

        return GraduationLevel.CANARY
