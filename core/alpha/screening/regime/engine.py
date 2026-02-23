from core.alpha.screening.models.screening_verdict import ScreeningVerdict
from core.alpha.screening.models.screening_layer import ScreeningLayer
from core.alpha.screening.models.screening_evidence import ScreeningEvidence

from core.alpha.screening.regime.metrics import (
    compute_volatility_ratio,
)
from core.alpha.screening.regime.artifacts import emit_regime_artifacts


def run_regime_admissibility(
    *,
    symbol: str,
    realized_vol: float,
    long_run_vol: float,
    trend_strength: float,
    structural_break: bool,
) -> ScreeningVerdict:
    """
    Deterministic regime admissibility evaluation.
    """

    vol_ratio = compute_volatility_ratio(realized_vol, long_run_vol)

    evidence = [
        ScreeningEvidence(
            metric="volatility_ratio",
            value=vol_ratio,
            threshold=1.5,
            interpretation="Current volatility vs long-run baseline",
        ),
        ScreeningEvidence(
            metric="trend_strength",
            value=trend_strength,
            threshold=0.3,
            interpretation="Trend persistence strength",
        ),
        ScreeningEvidence(
            metric="structural_break",
            value=float(structural_break),
            threshold=None,
            interpretation="Structural instability detected",
        ),
    ]

    # -----------------------------
    # Deterministic regime rule
    # -----------------------------
    if vol_ratio > 1.5 or trend_strength < 0.3 or structural_break:
        verdict = ScreeningVerdict(
            symbol=symbol,
            eligible=False,
            failed_layer=ScreeningLayer.REGIME_ADMISSIBILITY,
            confidence=0.15,
            evidence=evidence,
            explanation="Market regime not admissible for trading",
        )
    else:
        verdict = ScreeningVerdict(
            symbol=symbol,
            eligible=True,
            failed_layer=None,
            confidence=0.80,
            evidence=evidence,
            explanation="Market regime admissible",
        )

    emit_regime_artifacts(verdict)
    return verdict
