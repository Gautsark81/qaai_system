from modules.capital.allocator import CapitalAllocator


def test_allocator_produces_scaled_notional():
    alloc = CapitalAllocator()
    decision = alloc.allocate(
        equities=[100, 110, 90],
        volatility=0.03,
        cash_ratio=0.2,
        requested_notional=100_000,
    )

    assert decision.scale_factor <= 1.0
    assert decision.max_notional <= 100_000
