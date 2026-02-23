from core.v2.paper_capital.allocator import (
    PaperCapitalAllocator,
    AllocationInput,
)


def test_allocator_filters_by_ssr_and_regime():
    allocator = PaperCapitalAllocator(min_ssr=0.8)

    inputs = [
        AllocationInput("a", ssr=0.9, stability_stddev=0.1, regime_match=True),
        AllocationInput("b", ssr=0.7, stability_stddev=0.1, regime_match=True),  # low ssr
        AllocationInput("c", ssr=0.95, stability_stddev=0.2, regime_match=False),  # regime mismatch
    ]

    results = allocator.allocate(inputs)

    assert len(results) == 1
    assert results[0].strategy_id == "a"
    assert results[0].weight == 1.0


def test_allocator_normalizes_weights():
    allocator = PaperCapitalAllocator(min_ssr=0.5)

    inputs = [
        AllocationInput("a", ssr=1.0, stability_stddev=0.0, regime_match=True),
        AllocationInput("b", ssr=1.0, stability_stddev=1.0, regime_match=True),
    ]

    results = allocator.allocate(inputs)
    weights = {r.strategy_id: r.weight for r in results}

    assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert weights["a"] > weights["b"]


def test_allocator_no_eligible_returns_empty():
    allocator = PaperCapitalAllocator(min_ssr=0.9)

    inputs = [
        AllocationInput("a", ssr=0.5, stability_stddev=0.1, regime_match=True),
        AllocationInput("b", ssr=0.6, stability_stddev=0.1, regime_match=False),
    ]

    assert allocator.allocate(inputs) == []
