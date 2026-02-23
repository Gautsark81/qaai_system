from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


# ============================================================
# Shadow Alpha Diagnostics (Immutable, Observational)
# ============================================================

@dataclass(frozen=True)
class ShadowAlphaDiagnostics:
    """
    Pure observational alpha diagnostics.

    HARD LAWS:
    - Must NOT affect execution
    - Must NOT mutate intent
    - Must be deterministic
    - Must be read-only
    """

    confidence_score: float
    signal_quality: str
    regime_tag: str
    feature_attribution: Dict[str, float]
    probability_estimate: float
    explanation: str


# ============================================================
# Diagnostics Engine (Pure Function)
# ============================================================

def analyze_shadow_alpha(
    *,
    signal: Dict[str, Any],
    intent: Any,
) -> ShadowAlphaDiagnostics:
    """
    Analyze a shadow execution and produce alpha diagnostics.

    This function is intentionally simple in v1.
    Intelligence depth will increase later without changing the contract.
    """

    # --------------------------------------------------
    # Deterministic placeholder logic (v1)
    # --------------------------------------------------

    # Simple deterministic confidence heuristic
    confidence_score = 0.6

    # Categorize signal quality
    if confidence_score >= 0.75:
        signal_quality = "STRONG"
    elif confidence_score >= 0.5:
        signal_quality = "MODERATE"
    else:
        signal_quality = "WEAK"

    # Regime tagging (placeholder, deterministic)
    regime_tag = "UNKNOWN_REGIME"

    # Feature attribution (placeholder, deterministic)
    feature_attribution = {
        "price_action": 0.4,
        "volume": 0.3,
        "trend": 0.3,
    }

    # Probability estimate aligned with confidence (deterministic)
    probability_estimate = confidence_score

    explanation = (
        "Shadow alpha diagnostics computed using deterministic heuristics. "
        "No execution or capital influence applied."
    )

    return ShadowAlphaDiagnostics(
        confidence_score=confidence_score,
        signal_quality=signal_quality,
        regime_tag=regime_tag,
        feature_attribution=feature_attribution,
        probability_estimate=probability_estimate,
        explanation=explanation,
    )
