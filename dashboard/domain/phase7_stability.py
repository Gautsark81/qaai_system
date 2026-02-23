# dashboard/domain/phase7_stability.py

from typing import Dict, Any, List


def evaluate_stability(interpretation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase-7.4 — Interpretation Stability

    Detects panel drift.
    READ-ONLY
    DETERMINISTIC
    SNAPSHOT-ANCHORED
    """

    baseline = {
        "market_regime": "UNKNOWN",
        "risk_climate": "NEUTRAL",
        "strategy_stress": "LOW",
        "capital_pressure": "LOW",
    }

    changed: List[str] = []

    for panel, baseline_label in baseline.items():
        current = interpretation.get(panel, {})
        if current.get("label") != baseline_label:
            changed.append(panel)

    n = len(changed)

    if n == 0:
        status = "STABLE"
        drift_score = 0.0
    elif n <= 2:
        status = "DRIFTING"
        drift_score = min(1.0, 0.25 * n)
    else:
        status = "UNSTABLE"
        drift_score = 1.0

    explanation = (
        "Interpretation is stable with no panel drift."
        if n == 0
        else f"Interpretation drift detected across panels: {', '.join(changed)}."
    )

    return {
        "status": status,
        "drift_score": drift_score,
        "changed_panels": changed,
        "explanation": explanation,
    }
