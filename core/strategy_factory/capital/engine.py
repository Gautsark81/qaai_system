from datetime import datetime, timezone
import hashlib

from core.strategy_factory.capital.context import CapitalContext
from core.strategy_factory.capital.engine_models import CapitalEngineResult
from core.strategy_factory.capital.governance_audit import (
    build_capital_governance_audit,
)
from core.strategy_factory.capital.decision import decide_capital_eligibility

# 🚨 IMPORT MODULES — NOT FUNCTIONS (monkeypatch safe)
import core.strategy_factory.capital.governance_limits as governance_limits
import core.strategy_factory.capital.throttling as throttling
import core.strategy_factory.capital.allocation_policy as allocation_policy


# ==========================================================
# Deterministic Governance Chain Builder
# ==========================================================

def _build_governance_chain_id(
    *,
    strategy_dna: str,
    requested_capital: float,
    created_at: datetime,
    governance_reason: str,
) -> str:
    """
    Deterministic governance chain ID.
    Replay-safe.
    No randomness.
    """

    payload = (
        f"{strategy_dna}|"
        f"{requested_capital}|"
        f"{created_at.isoformat()}|"
        f"{governance_reason}"
    )

    return hashlib.sha256(payload.encode()).hexdigest()


def run_capital_engine(
    *,
    strategy_dna: str,
    requested_capital: float,
    limits,
    context: CapitalContext,
    now: datetime | None = None,
) -> CapitalEngineResult:
    """
    Capital engine orchestration.

    STRICT ORDER:
    1. Governance   (hard stop)
    2. Throttling   (hard stop)
    3. Eligibility (signal only at C4)
    4. Allocation
    """

    created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    now = now or created_at

    # -------------------------------------------------
    # 1️⃣ Governance
    # -------------------------------------------------
    governance = governance_limits.decide_capital_governance_limits(
        strategy_dna=strategy_dna,
        requested_capital=requested_capital,
        strategy_current_capital=context.strategy_current_capital,
        global_capital_used=context.global_capital_used,
        limits=limits,
    )

    governance_audit = build_capital_governance_audit(
        strategy_dna=strategy_dna,
        requested_capital=requested_capital,
        decision=governance,
        limits=limits,
        created_at=created_at,
    )

    governance_chain_id = _build_governance_chain_id(
        strategy_dna=strategy_dna,
        requested_capital=requested_capital,
        created_at=created_at,
        governance_reason=governance.reason,
    )

    if not governance.allowed:
        return CapitalEngineResult(
            governance=governance,
            governance_audit=governance_audit,
            throttle=None,
            allocation=None,
        )

    # -------------------------------------------------
    # 2️⃣ Throttling
    # -------------------------------------------------
    throttle = throttling.evaluate_capital_throttle(
        strategy_dna=strategy_dna,
        requested_capital=requested_capital,
        last_allocation_at=getattr(context, "last_allocation_at", None),
        cooldown_seconds=getattr(context, "cooldown_seconds", 0),
        now=now,
        governance_chain_id=governance_chain_id,
    )

    if not throttle.allowed:
        return CapitalEngineResult(
            governance=governance,
            governance_audit=governance_audit,
            throttle=throttle,
            allocation=None,
        )

    # -------------------------------------------------
    # 3️⃣ Eligibility (non-blocking at C4)
    # -------------------------------------------------
    eligibility = decide_capital_eligibility(
        lifecycle_state="LIVE",
        promotion_level="LIVE_ELIGIBLE",
        health="HEALTHY",
    )

    # -------------------------------------------------
    # 4️⃣ Allocation
    # -------------------------------------------------
    allocation = allocation_policy.apply_allocation_policy(
        eligibility=eligibility,
        requested_capital=requested_capital,
        max_per_strategy=limits.per_strategy_cap,
        global_cap_remaining=limits.global_cap - context.global_capital_used,
    )

    return CapitalEngineResult(
        governance=governance,
        governance_audit=governance_audit,
        throttle=throttle,
        allocation=allocation,
    )