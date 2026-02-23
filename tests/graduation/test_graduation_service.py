from domain.graduation.graduation_service import GraduationService
from domain.graduation.graduation_level import GraduationLevel
from domain.graduation.strategy_performance_snapshot import (
    StrategyPerformanceSnapshot
)
from domain.graduation.graduation_policy import GraduationPolicy


def test_graduation_service_promotes():
    snap = StrategyPerformanceSnapshot("S1", 0.8, 0.05, 60, 500)
    policy = GraduationPolicy(0.75, 30, 0.12, 200)

    level = GraduationService.evaluate(snap, policy)
    assert level == GraduationLevel.PRODUCTION
