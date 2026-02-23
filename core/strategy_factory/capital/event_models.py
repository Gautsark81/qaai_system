from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.strategy_factory.capital.memory import CapitalAllocationMemory


# ============================================================
# Policy snapshot (governance-only)
# ============================================================

@dataclass(frozen=True)
class CapitalPolicySnapshot:
    """
    Immutable snapshot of capital policy inputs at decision time.
    """

    requested_capital: float
    max_per_strategy: float
    global_cap_remaining: float


# ============================================================
# Capital allocation audit event
# ============================================================

@dataclass(frozen=True)
class CapitalEventAudit:
    """
    Immutable audit record for a capital allocation event.

    HARD GUARANTEES:
    - Deterministic
    - Pure data
    - No behavior
    - Replay-safe
    """

    strategy_dna: str

    # Decisions (opaque, not typed here)
    eligibility: object
    allocation: object

    # Governance inputs
    policy_snapshot: CapitalPolicySnapshot

    # Memory evolution
    memory_before: Optional[CapitalAllocationMemory]
    memory_after: CapitalAllocationMemory

    # Metadata
    created_at: datetime
    fingerprint: str
