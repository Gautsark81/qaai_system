# core/capital/evidence_emitter.py

from datetime import datetime, timezone
from typing import Dict

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.decision_store import DecisionEvidenceStore
from core.evidence.checksum import compute_checksum

from core.capital.contracts import (
    StrategyCapitalSignal,
    CapitalEvidenceContext,
)

from core.capital.allocator_v3.contracts import (
    CapitalDecisionArtifact,
    AllocationValue,
)


# ======================================================
# 🧾 CAPITAL DECISION EVIDENCE (V3)
# ======================================================

def emit_capital_decision_evidence(
    *,
    decision: CapitalDecisionArtifact,
    context: CapitalEvidenceContext,
    store: DecisionEvidenceStore,
) -> None:
    """
    Emit capital allocation evidence.

    Design rules:
    - NEVER mutates allocation
    - NEVER raises
    - Purely observational
    """

    timestamp = datetime.now(timezone.utc)

    for strategy_id, allocation in decision.allocations.items():
        # AllocationValue → float (CRITICAL FIX)
        weight = (
            allocation.allocated_fraction
            if isinstance(allocation, AllocationValue)
            else float(allocation)
        )

        factors = [
            ("strategy_id", strategy_id),
            ("approved_weight", weight),
        ]

        if decision.attribution and strategy_id in decision.attribution:
            a = decision.attribution[strategy_id]
            factors.extend(
                [
                    ("raw_fitness", a.raw_fitness),
                    ("fragility_penalty", a.fragility_penalty),
                    ("regime_throttle", a.regime_throttle),
                    ("final_weight", a.final_weight),
                ]
            )

        if context.capital_available is not None:
            factors.append(("capital_available", context.capital_available))

        checksum = compute_checksum(tuple(factors))

        store.append(
            DecisionEvidence(
                decision_id=checksum,
                decision_type="CAPITAL_ALLOCATION",
                timestamp=timestamp,
                strategy_id=strategy_id,
                approved_weight=weight,
                rationale="Capital allocation decision",
                factors=tuple(factors),
                checksum=checksum,
            )
        )


# ======================================================
# 📊 LEGACY / PORTFOLIO-LEVEL EVIDENCE
# ======================================================

def emit_capital_allocation_evidence(
    *,
    signals: Dict[str, StrategyCapitalSignal],
    allocations: Dict[str, float],
    capital_available: float,
    store: DecisionEvidenceStore,
) -> None:
    """
    Emit read-only portfolio capital allocation evidence.

    Guarantees:
    - No allocator feedback
    - No execution coupling
    """

    timestamp = datetime.now(timezone.utc)

    for strategy_id, weight in allocations.items():
        signal = signals.get(strategy_id)
        if signal is None:
            continue

        factors = (
            ("strategy_id", strategy_id),
            ("approved_weight", weight),
            ("ssr", signal.ssr),
            ("confidence", signal.confidence),
            ("regime_score", signal.regime_score),
        )

        checksum = compute_checksum(fields=factors)

        store.append(
            DecisionEvidence(
                decision_id=checksum,
                decision_type="CAPITAL_ALLOC",
                timestamp=timestamp,
                strategy_id=strategy_id,
                approved_weight=weight,
                capital_available=capital_available,
                ssr=signal.ssr,
                confidence=signal.confidence,
                regime_confidence=signal.regime_score,
                rationale="Portfolio capital allocation",
                factors=factors,
                checksum=checksum,
            )
        )
