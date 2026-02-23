import pytest
from core.institution.capital_partition.models import CapitalEnvelope
from core.institution.capital_partition.allocator import CapitalPartitionAllocator


def test_register_and_view_allocation():
    allocator = CapitalPartitionAllocator()

    allocator.register_envelope(
        envelope=CapitalEnvelope(portfolio_id="P1", max_capital=1000.0)
    )

    view = allocator.allocation_view(portfolio_id="P1")
    assert view.max_capital == 1000.0
    assert view.used_capital == 0.0
    assert view.remaining_capital == 1000.0


def test_record_usage_within_envelope():
    allocator = CapitalPartitionAllocator()
    allocator.register_envelope(
        envelope=CapitalEnvelope(portfolio_id="P1", max_capital=500.0)
    )

    allocator.record_usage(portfolio_id="P1", amount=200.0)
    view = allocator.allocation_view(portfolio_id="P1")

    assert view.used_capital == 200.0
    assert view.remaining_capital == 300.0


def test_exceeding_envelope_raises():
    allocator = CapitalPartitionAllocator()
    allocator.register_envelope(
        envelope=CapitalEnvelope(portfolio_id="P1", max_capital=300.0)
    )

    allocator.record_usage(portfolio_id="P1", amount=250.0)

    with pytest.raises(ValueError):
        allocator.record_usage(portfolio_id="P1", amount=100.0)


def test_portfolios_are_isolated():
    allocator = CapitalPartitionAllocator()

    allocator.register_envelope(
        envelope=CapitalEnvelope(portfolio_id="P1", max_capital=300.0)
    )
    allocator.register_envelope(
        envelope=CapitalEnvelope(portfolio_id="P2", max_capital=1000.0)
    )

    allocator.record_usage(portfolio_id="P2", amount=900.0)

    view1 = allocator.allocation_view(portfolio_id="P1")
    view2 = allocator.allocation_view(portfolio_id="P2")

    assert view1.used_capital == 0.0
    assert view2.remaining_capital == 100.0
