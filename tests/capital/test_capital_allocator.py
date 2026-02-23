from modules.capital.allocator import CapitalAllocator
from modules.capital.policies import CapitalPolicy


def test_neutral_scaling_no_drawdown():
    alloc = CapitalAllocator()
    equities = [100, 110, 120]

    decision = alloc.allocate(
        equities=equities,
        requested_notional=100_000,
    )

    assert decision.approved is True
    assert decision.scale_factor == 1.0
    assert decision.max_notional == 100_000


def test_scaling_with_drawdown():
    alloc = CapitalAllocator(
        policy=CapitalPolicy(max_drawdown_pct=0.20, min_scale=0.25)
    )
    equities = [100, 120, 90]  # 25% DD

    decision = alloc.allocate(
        equities=equities,
        requested_notional=100_000,
    )

    assert decision.scale_factor == 0.25
    assert decision.max_notional == 25_000
