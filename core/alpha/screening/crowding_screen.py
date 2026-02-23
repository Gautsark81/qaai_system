# core/alpha/screening/crowding_screen.py

from typing import List

from .crowding_evidence import CrowdingRiskEvidence
from .crowding_verdict import CrowdingRiskVerdict


INSTITUTIONAL_CROWDING_BLOCKERS = {
    "fii_overcrowding",
    "dii_overcrowding",
    "large_holder_concentration",
}

STRATEGY_CONSENSUS_BLOCKERS = {
    "strategy_saturation",
    "consensus_trade",
    "model_homogeneity",
}

POSITIONING_FRAGILITY_BLOCKERS = {
    "one_way_positioning",
    "correlated_exit_risk",
    "liquidity_cliff_exit",
}


def run_crowding_risk_screen(
    *,
    symbol: str,
    evidence: CrowdingRiskEvidence,
) -> CrowdingRiskVerdict:
    blocked: List[str] = []
    reasons: List[str] = []

    # 1. Institutional crowding
    if any(
        flag in INSTITUTIONAL_CROWDING_BLOCKERS
        for flag in evidence.institutional_crowding_flags
    ):
        blocked.append("institutional_crowding")
        reasons.append("Blocked due to institutional crowding risk")

    # 2. Strategy consensus saturation
    if any(
        flag in STRATEGY_CONSENSUS_BLOCKERS
        for flag in evidence.strategy_consensus_flags
    ):
        blocked.append("strategy_consensus")
        reasons.append("Blocked due to strategy consensus saturation")

    # 3. One-way positioning fragility
    if any(
        flag in POSITIONING_FRAGILITY_BLOCKERS
        for flag in evidence.positioning_fragility_flags
    ):
        blocked.append("positioning_fragility")
        reasons.append("Blocked due to one-way positioning fragility")

    if blocked:
        return CrowdingRiskVerdict(
            passed=False,
            reasons=tuple(reasons),
            blocked_dimensions=tuple(blocked),
        )

    return CrowdingRiskVerdict(
        passed=True,
        reasons=("Crowding risk screening passed",),
        blocked_dimensions=(),
    )
