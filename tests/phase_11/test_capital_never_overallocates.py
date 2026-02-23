from model_ops.capital.allocation_engine import (
    AllocationEngine,
    AllocationInput,
)


def test_allocation_never_exceeds_total_capital():
    """
    Hard safety invariant:
    Allocation must never exceed total capital (1.0),
    regardless of input weights.
    """

    engine = AllocationEngine()

    inp = AllocationInput(
        weights={
            "s1": 0.9,
            "s2": 0.9,
            "s3": 0.9,
        },
        capital=1.0,
    )

    result = engine.allocate(inp)

    assert result.total_allocated <= 1.0
