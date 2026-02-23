from domain.graduation.graduation_gate import GraduationGate
from domain.graduation.strategy_performance_snapshot import (
    StrategyPerformanceSnapshot
)
from domain.graduation.graduation_policy import GraduationPolicy


def test_graduation_gate_blocks_low_ssr():
    snap = StrategyPerformanceSnapshot("S1", 0.6, 0.05, 40, 300)
    policy = GraduationPolicy(0.75, 30, 0.12, 200)

    assert GraduationGate.allow(snap, policy) is False
