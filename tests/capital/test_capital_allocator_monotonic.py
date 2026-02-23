from modules.capital.allocator import CapitalAllocator


def test_monotonic_scale_with_worsening_drawdown():
    alloc = CapitalAllocator()
    req = 100_000

    eq_small_dd = [100, 110, 105]
    eq_large_dd = [100, 120, 90]

    d1 = alloc.allocate(
        equities=eq_small_dd,
        requested_notional=req,
    )
    d2 = alloc.allocate(
        equities=eq_large_dd,
        requested_notional=req,
    )

    assert d2.scale_factor <= d1.scale_factor
    assert d2.max_notional <= d1.max_notional
