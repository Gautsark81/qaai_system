from datetime import datetime
import copy

from core.strategy_factory.capital.audit_event import build_capital_event_audit
from core.strategy_factory.capital.allocation_models import (
    CapitalEligibilityDecision,
    CapitalAllocationDecision,
)
from core.strategy_factory.capital.memory import CapitalAllocationMemory
from core.strategy_factory.capital.event_models import (
    CapitalEventAudit,
    CapitalPolicySnapshot,
)


def _make_eligibility(ok: bool = True):
    return CapitalEligibilityDecision(
        eligible=ok,
        reason="eligible" if ok else "not eligible",
    )


def _make_allocation(amount: float):
    return CapitalAllocationDecision(
        allocated_capital=amount,
        reason="within limits" if amount > 0 else "denied",
    )


def _make_policy():
    return CapitalPolicySnapshot(
        requested_capital=100_000,
        max_per_strategy=50_000,
        global_cap_remaining=1_000_000,
    )


# ============================================================
# C3.5-T1 — Deterministic audit event
# ============================================================

def test_capital_event_audit_is_deterministic():
    ts = datetime(2025, 1, 1)

    eligibility = _make_eligibility(True)
    allocation = _make_allocation(50_000)
    policy = _make_policy()

    audit1 = build_capital_event_audit(
        strategy_dna="STRAT-001",
        eligibility=eligibility,
        allocation=allocation,
        memory_before=None,
        policy_snapshot=policy,
        created_at=ts,
    )

    audit2 = build_capital_event_audit(
        strategy_dna="STRAT-001",
        eligibility=eligibility,
        allocation=allocation,
        memory_before=None,
        policy_snapshot=policy,
        created_at=ts,
    )

    assert audit1 == audit2


# ============================================================
# C3.5-T2 — Memory delta is applied correctly
# ============================================================

def test_capital_event_audit_updates_memory_correctly():
    ts = datetime(2025, 1, 1)

    prev_memory = CapitalAllocationMemory(
        last_allocated_capital=40_000,
        last_allocation_at=ts,
        allocation_count=1,
        cumulative_allocated=40_000,
        rejection_count=0,
    )

    audit = build_capital_event_audit(
        strategy_dna="STRAT-002",
        eligibility=_make_eligibility(True),
        allocation=_make_allocation(30_000),
        memory_before=prev_memory,
        policy_snapshot=_make_policy(),
        created_at=ts,
    )

    after = audit.memory_after

    assert after.allocation_count == 2
    assert after.cumulative_allocated == 70_000
    assert after.last_allocated_capital == 30_000
    assert after.rejection_count == 0


# ============================================================
# C3.5-T3 — Rejections increment rejection counter
# ============================================================

def test_capital_event_audit_rejection_increments_counter():
    ts = datetime(2025, 1, 1)

    prev_memory = CapitalAllocationMemory(
        last_allocated_capital=25_000,
        last_allocation_at=ts,
        allocation_count=1,
        cumulative_allocated=25_000,
        rejection_count=0,
    )

    audit = build_capital_event_audit(
        strategy_dna="STRAT-003",
        eligibility=_make_eligibility(False),
        allocation=_make_allocation(0.0),
        memory_before=prev_memory,
        policy_snapshot=_make_policy(),
        created_at=ts,
    )

    after = audit.memory_after

    assert after.allocation_count == 1
    assert after.cumulative_allocated == 25_000
    assert after.rejection_count == 1


# ============================================================
# C3.5-T4 — Inputs are NOT mutated
# ============================================================

def test_capital_event_audit_does_not_mutate_inputs():
    ts = datetime(2025, 1, 1)

    eligibility = _make_eligibility(True)
    allocation = _make_allocation(50_000)
    policy = _make_policy()
    memory = CapitalAllocationMemory(
        last_allocated_capital=10_000,
        last_allocation_at=ts,
        allocation_count=1,
        cumulative_allocated=10_000,
        rejection_count=0,
    )

    snap = copy.deepcopy((eligibility, allocation, policy, memory))

    build_capital_event_audit(
        strategy_dna="STRAT-004",
        eligibility=eligibility,
        allocation=allocation,
        memory_before=memory,
        policy_snapshot=policy,
        created_at=ts,
    )

    assert (eligibility, allocation, policy, memory) == snap


# ============================================================
# C3.5-T5 — Fingerprint is present and stable
# ============================================================

def test_capital_event_audit_has_fingerprint():
    ts = datetime(2025, 1, 1)

    audit = build_capital_event_audit(
        strategy_dna="STRAT-005",
        eligibility=_make_eligibility(True),
        allocation=_make_allocation(20_000),
        memory_before=None,
        policy_snapshot=_make_policy(),
        created_at=ts,
    )

    assert isinstance(audit.fingerprint, str)
    assert len(audit.fingerprint) >= 16
