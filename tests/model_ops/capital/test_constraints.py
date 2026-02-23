import pytest

from qaai_system.model_ops.capital import (
    CapitalLadder,
    CapitalStep,
    CapitalAllocator,
    CapitalConstraintError,
)


def test_total_capital_never_exceeds_one():
    ladder = CapitalLadder([
        CapitalStep("a", 0.6),
        CapitalStep("b", 0.5),
    ])

    allocator = CapitalAllocator(ladder)

    allocator.assign(model_id="m1", step_index=0)

    with pytest.raises(CapitalConstraintError):
        allocator.assign(model_id="m2", step_index=1)
