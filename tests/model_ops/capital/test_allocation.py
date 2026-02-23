import pytest
from datetime import datetime

from qaai_system.model_ops.capital import (
    CapitalLadder,
    CapitalStep,
    CapitalAllocator,
    CapitalConstraintError,
)


def test_allocator_assigns_capital():
    ladder = CapitalLadder([
        CapitalStep("canary", 0.2),
        CapitalStep("full", 1.0),
    ])

    allocator = CapitalAllocator(ladder)

    allocation = allocator.assign(model_id="m1", step_index=0)

    assert allocation.model_id == "m1"
    assert allocation.weight == 0.2
    assert allocation.ladder_step == "canary"
    assert isinstance(allocation.updated_at, datetime)


def test_allocator_enforces_total_capital_constraint():
    ladder = CapitalLadder([
        CapitalStep("a", 0.6),
        CapitalStep("b", 0.5),
    ])

    allocator = CapitalAllocator(ladder)

    allocator.assign(model_id="m1", step_index=0)

    with pytest.raises(CapitalConstraintError):
        allocator.assign(model_id="m2", step_index=1)


def test_allocator_get_and_all():
    ladder = CapitalLadder([
        CapitalStep("canary", 0.3),
    ])

    allocator = CapitalAllocator(ladder)
    allocator.assign(model_id="m1", step_index=0)

    alloc = allocator.get("m1")
    all_allocs = allocator.all()

    assert alloc.weight == 0.3
    assert "m1" in all_allocs
