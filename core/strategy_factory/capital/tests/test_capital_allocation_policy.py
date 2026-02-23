from core.strategy_factory.capital.models import CapitalEligibilityDecision
from core.strategy_factory.capital.allocation_policy import apply_allocation_policy
from core.strategy_factory.capital.allocation_models import CapitalAllocationDecision


def test_allocation_zero_when_not_eligible():
    eligibility = CapitalEligibilityDecision(
        eligible=False,
        reason="not eligible",
    )

    decision = apply_allocation_policy(
        eligibility=eligibility,
        requested_capital=100_000,
        max_per_strategy=50_000,
        global_cap_remaining=1_000_000,
    )

    assert decision.approved_capital == 0
    assert "not eligible" in decision.reason.lower()


def test_allocation_capped_by_max_per_strategy():
    eligibility = CapitalEligibilityDecision(
        eligible=True,
        reason="eligible",
    )

    decision = apply_allocation_policy(
        eligibility=eligibility,
        requested_capital=100_000,
        max_per_strategy=50_000,
        global_cap_remaining=1_000_000,
    )

    assert decision.approved_capital == 50_000
    assert "max per strategy" in decision.reason.lower()


def test_allocation_capped_by_global_remaining():
    eligibility = CapitalEligibilityDecision(
        eligible=True,
        reason="eligible",
    )

    decision = apply_allocation_policy(
        eligibility=eligibility,
        requested_capital=100_000,
        max_per_strategy=200_000,
        global_cap_remaining=30_000,
    )

    assert decision.approved_capital == 30_000
    assert "global cap" in decision.reason.lower()


def test_allocation_full_when_within_limits():
    eligibility = CapitalEligibilityDecision(
        eligible=True,
        reason="eligible",
    )

    decision = apply_allocation_policy(
        eligibility=eligibility,
        requested_capital=40_000,
        max_per_strategy=50_000,
        global_cap_remaining=1_000_000,
    )

    assert decision.approved_capital == 40_000
    assert "approved" in decision.reason.lower()
