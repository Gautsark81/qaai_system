from core.alpha.screening.models.screening_verdict import ScreeningVerdict
from core.alpha.screening.models.screening_layer import ScreeningLayer
from core.alpha.screening.models.screening_evidence import ScreeningEvidence

from core.alpha.screening.liquidity.metrics import (
    compute_order_pct_adv,
    compute_exit_days,
)
from core.alpha.screening.liquidity.artifacts import emit_liquidity_artifacts


def run_liquidity_survivability(
    *,
    symbol: str,
    adv_value: float,
    order_value: float,
    volatility_spike: bool,
) -> ScreeningVerdict:
    """
    Deterministic liquidity survivability evaluation.
    """

    order_pct_adv = compute_order_pct_adv(order_value, adv_value)
    exit_days = compute_exit_days(order_pct_adv, volatility_spike)

    evidence = [
        ScreeningEvidence(
            metric="order_pct_adv",
            value=order_pct_adv,
            threshold=0.05,
            interpretation="Order size relative to average traded value",
        ),
        ScreeningEvidence(
            metric="exit_days",
            value=exit_days,
            threshold=3.0,
            interpretation="Estimated days required to exit position",
        ),
        ScreeningEvidence(
            metric="volatility_spike",
            value=float(volatility_spike),
            threshold=None,
            interpretation="Stress regime detected",
        ),
    ]

    # -----------------------------
    # Deterministic decision rule
    # -----------------------------
    if order_pct_adv > 0.05 or exit_days > 3.0:
        verdict = ScreeningVerdict(
            symbol=symbol,
            eligible=False,
            failed_layer=ScreeningLayer.LIQUIDITY_SURVIVABILITY,
            confidence=0.10,
            evidence=evidence,
            explanation="Liquidity insufficient under stress conditions",
        )
    else:
        verdict = ScreeningVerdict(
            symbol=symbol,
            eligible=True,
            failed_layer=None,
            confidence=0.85,
            evidence=evidence,
            explanation="Liquidity sufficient for expected execution",
        )

    emit_liquidity_artifacts(verdict)
    return verdict
