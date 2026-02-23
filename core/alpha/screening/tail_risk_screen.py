# core/alpha/screening/tail_risk_screen.py

from typing import List

from .tail_risk_evidence import TailRiskEvidence
from .tail_risk_verdict import TailRiskVerdict


CRISIS_REGIME_BLOCKERS = {
    "crisis_dependency",
    "crisis_only_profitability",
}

VOLATILITY_EXPLOSION_BLOCKERS = {
    "vol_explosion_fragility",
    "volatility_spike_failure",
}

GAP_RISK_BLOCKERS = {
    "stress_gap_exposure",
    "overnight_gap_risk",
}

CORRELATION_BREAKDOWN_BLOCKERS = {
    "correlation_spike_risk",
    "diversification_collapse",
}

CONVEXITY_FAILURE_BLOCKERS = {
    "drawdown_convexity_failure",
    "left_tail_convexity_loss",
}


def run_tail_risk_screen(
    *,
    symbol: str,
    evidence: TailRiskEvidence,
) -> TailRiskVerdict:
    blocked: List[str] = []
    reasons: List[str] = []

    # 1. Crisis regime exposure
    if any(flag in CRISIS_REGIME_BLOCKERS for flag in evidence.crisis_regime_flags):
        blocked.append("crisis_regime")
        reasons.append("Blocked due to crisis regime exposure")

    # 2. Volatility explosion fragility
    if any(
        flag in VOLATILITY_EXPLOSION_BLOCKERS
        for flag in evidence.volatility_explosion_flags
    ):
        blocked.append("volatility_explosion")
        reasons.append("Blocked due to volatility explosion fragility")

    # 3. Gap-risk under stress
    if any(flag in GAP_RISK_BLOCKERS for flag in evidence.gap_risk_flags):
        blocked.append("gap_risk")
        reasons.append("Blocked due to gap-risk under stress")

    # 4. Correlation breakdown risk
    if any(
        flag in CORRELATION_BREAKDOWN_BLOCKERS
        for flag in evidence.correlation_breakdown_flags
    ):
        blocked.append("correlation_breakdown")
        reasons.append("Blocked due to correlation breakdown risk")

    # 5. Convexity / drawdown failure
    if any(
        flag in CONVEXITY_FAILURE_BLOCKERS
        for flag in evidence.convexity_failure_flags
    ):
        blocked.append("convexity_failure")
        reasons.append("Blocked due to convexity / drawdown failure")

    if blocked:
        return TailRiskVerdict(
            passed=False,
            reasons=tuple(reasons),
            blocked_dimensions=tuple(blocked),
        )

    return TailRiskVerdict(
        passed=True,
        reasons=("Tail risk screening passed",),
        blocked_dimensions=(),
    )
