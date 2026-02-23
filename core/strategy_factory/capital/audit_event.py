from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from core.strategy_factory.capital.memory import CapitalAllocationMemory
from core.strategy_factory.capital.event_models import (
    CapitalEventAudit,
    CapitalPolicySnapshot,
)
from core.evidence.checksum import compute_checksum


def build_capital_event_audit(
    *,
    strategy_dna: str,
    eligibility: Any,
    allocation: Any,
    memory_before: Optional[CapitalAllocationMemory],
    policy_snapshot: CapitalPolicySnapshot,
    created_at: datetime,
) -> CapitalEventAudit:
    """
    Build a deterministic, immutable capital allocation event audit.

    Governance guarantees:
    - Pure function
    - Deterministic fingerprint
    - Explicit memory evolution
    - No mutation
    - No side effects
    """

    allocated = float(getattr(allocation, "allocated_capital", 0.0))

    # --------------------------------------------------
    # 1️⃣ Compute memory_after (pure, deterministic)
    # --------------------------------------------------

    if memory_before is None:
        if allocated > 0:
            memory_after = CapitalAllocationMemory(
                last_allocated_capital=allocated,
                last_allocation_at=created_at,
                allocation_count=1,
                cumulative_allocated=allocated,
                rejection_count=0,
            )
        else:
            memory_after = CapitalAllocationMemory(
                last_allocated_capital=0.0,
                last_allocation_at=None,
                allocation_count=0,
                cumulative_allocated=0.0,
                rejection_count=1,
            )
    else:
        if allocated > 0:
            memory_after = CapitalAllocationMemory(
                last_allocated_capital=allocated,
                last_allocation_at=created_at,
                allocation_count=memory_before.allocation_count + 1,
                cumulative_allocated=(
                    memory_before.cumulative_allocated + allocated
                ),
                rejection_count=memory_before.rejection_count,
            )
        else:
            memory_after = CapitalAllocationMemory(
                last_allocated_capital=memory_before.last_allocated_capital,
                last_allocation_at=memory_before.last_allocation_at,
                allocation_count=memory_before.allocation_count,
                cumulative_allocated=memory_before.cumulative_allocated,
                rejection_count=memory_before.rejection_count + 1,
            )

    # --------------------------------------------------
    # 2️⃣ Deterministic fingerprint
    # --------------------------------------------------

    fingerprint = compute_checksum(
        fields=[
            ("strategy_dna", strategy_dna),
            ("created_at", created_at.isoformat()),

            ("eligibility.eligible", getattr(eligibility, "eligible")),
            ("eligibility.reason", getattr(eligibility, "reason")),

            ("allocation.allocated_capital", allocated),
            ("allocation.reason", getattr(allocation, "reason")),

            ("policy.requested_capital", policy_snapshot.requested_capital),
            ("policy.max_per_strategy", policy_snapshot.max_per_strategy),
            ("policy.global_cap_remaining", policy_snapshot.global_cap_remaining),

            ("memory_before.allocation_count",
             memory_before.allocation_count if memory_before else None),
            ("memory_before.cumulative_allocated",
             memory_before.cumulative_allocated if memory_before else None),
            ("memory_before.rejection_count",
             memory_before.rejection_count if memory_before else None),

            ("memory_after.allocation_count", memory_after.allocation_count),
            ("memory_after.cumulative_allocated", memory_after.cumulative_allocated),
            ("memory_after.rejection_count", memory_after.rejection_count),
        ]
    )

    # --------------------------------------------------
    # 3️⃣ Assemble audit record
    # --------------------------------------------------

    return CapitalEventAudit(
        strategy_dna=strategy_dna,
        eligibility=eligibility,
        allocation=allocation,
        policy_snapshot=policy_snapshot,
        memory_before=memory_before,
        memory_after=memory_after,
        created_at=created_at,
        fingerprint=fingerprint,
    )
