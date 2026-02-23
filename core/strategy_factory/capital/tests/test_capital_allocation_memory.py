from datetime import datetime, timedelta

from core.strategy_factory.capital.allocation_models import (
    CapitalAllocationDecision,
)
from core.strategy_factory.capital.memory import (
    CapitalAllocationMemory,
    update_capital_allocation_memory,
)


def test_first_allocation_creates_memory():
    ts = datetime(2025, 1, 1)

    decision = CapitalAllocationDecision(
        allocated_capital=50_000,
        reason="within limits",
    )

    memory = update_capital_allocation_memory(
        previous=None,
        allocation=decision,
        created_at=ts,
    )

    assert memory.last_allocated_capital == 50_000
    assert memory.allocation_count == 1
    assert memory.cumulative_allocated == 50_000
    assert memory.rejection_count == 0
    assert memory.last_allocation_at == ts


def test_subsequent_allocation_accumulates():
    ts1 = datetime(2025, 1, 1)
    ts2 = ts1 + timedelta(days=1)

    prev = CapitalAllocationMemory(
        last_allocated_capital=40_000,
        last_allocation_at=ts1,
        allocation_count=1,
        cumulative_allocated=40_000,
        rejection_count=0,
    )

    decision = CapitalAllocationDecision(
        allocated_capital=30_000,
        reason="within limits",
    )

    memory = update_capital_allocation_memory(
        previous=prev,
        allocation=decision,
        created_at=ts2,
    )

    assert memory.last_allocated_capital == 30_000
    assert memory.allocation_count == 2
    assert memory.cumulative_allocated == 70_000
    assert memory.rejection_count == 0
    assert memory.last_allocation_at == ts2


def test_zero_allocation_is_recorded():
    ts = datetime(2025, 1, 1)

    decision = CapitalAllocationDecision(
        allocated_capital=0.0,
        reason="not eligible",
    )

    memory = update_capital_allocation_memory(
        previous=None,
        allocation=decision,
        created_at=ts,
    )

    assert memory.last_allocated_capital == 0.0
    assert memory.allocation_count == 1
    assert memory.cumulative_allocated == 0.0
    assert memory.rejection_count == 1
    assert memory.last_allocation_at == ts


def test_rejection_increments_rejection_count():
    ts1 = datetime(2025, 1, 1)
    ts2 = ts1 + timedelta(days=1)

    prev = CapitalAllocationMemory(
        last_allocated_capital=25_000,
        last_allocation_at=ts1,
        allocation_count=1,
        cumulative_allocated=25_000,
        rejection_count=0,
    )

    decision = CapitalAllocationDecision(
        allocated_capital=0.0,
        reason="global cap exhausted",
    )

    memory = update_capital_allocation_memory(
        previous=prev,
        allocation=decision,
        created_at=ts2,
    )

    assert memory.last_allocated_capital == 0.0
    assert memory.allocation_count == 2
    assert memory.cumulative_allocated == 25_000
    assert memory.rejection_count == 1
    assert memory.last_allocation_at == ts2


def test_memory_is_deterministic_and_immutable():
    ts = datetime(2025, 1, 1)

    prev = CapitalAllocationMemory(
        last_allocated_capital=10_000,
        last_allocation_at=ts,
        allocation_count=1,
        cumulative_allocated=10_000,
        rejection_count=0,
    )

    decision = CapitalAllocationDecision(
        allocated_capital=5_000,
        reason="within limits",
    )

    mem1 = update_capital_allocation_memory(
        previous=prev,
        allocation=decision,
        created_at=ts,
    )

    mem2 = update_capital_allocation_memory(
        previous=prev,
        allocation=decision,
        created_at=ts,
    )

    assert mem1 == mem2
    assert prev.allocation_count == 1  # original object unchanged
