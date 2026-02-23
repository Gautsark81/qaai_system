from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.strategy_factory.capital.ledger_models import CapitalLedgerEntry
from core.strategy_factory.capital.capital_state_hash import (
    compute_capital_state_hash,
)


# ============================================================
# C4.8 — Capital Replay Verification Barrier
# ============================================================

@dataclass(frozen=True)
class CapitalReplayVerificationReport:
    """
    Immutable replay verification result.

    Guarantees:
    - Deterministic
    - Governance-only
    - No side effects
    """

    pre_replay_hash: str
    post_replay_hash: str
    is_consistent: bool


def verify_capital_replay(
    *,
    pre_replay_ledger: Iterable[CapitalLedgerEntry],
    post_replay_ledger: Iterable[CapitalLedgerEntry],
    strict: bool = False,
) -> CapitalReplayVerificationReport:
    """
    Verifies that capital ledger state hash is identical
    before and after replay.

    Invariants:
    - Order independent
    - Deterministic
    - No mutation
    - Pure verification layer
    """

    pre_hash = compute_capital_state_hash(pre_replay_ledger)
    post_hash = compute_capital_state_hash(post_replay_ledger)

    consistent = pre_hash == post_hash

    if strict and not consistent:
        raise RuntimeError(
            "Capital replay verification failed: "
            f"{pre_hash} != {post_hash}"
        )

    return CapitalReplayVerificationReport(
        pre_replay_hash=pre_hash,
        post_replay_hash=post_hash,
        is_consistent=consistent,
    )