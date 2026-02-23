# dashboard/domain/phase7_consistency.py

from typing import Dict, Any, List


def evaluate_consistency(interpretation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase-7.2 cross-panel consistency evaluator.

    PURE FUNCTION
    DETERMINISTIC
    NO SIDE EFFECTS
    """

    violations: List[Dict[str, Any]] = []

    def label(panel: str) -> str:
        return interpretation[panel]["label"]

    # ─────────────────────────────────────────────
    # Rule C-1: Risk vs Regime
    # ─────────────────────────────────────────────
    if (
        label("market_regime") == "RISK_OFF"
        and label("risk_climate") == "LOW"
    ):
        violations.append({
            "rule_id": "C-1",
            "panels": ["market_regime", "risk_climate"],
            "description": "Risk-off regime contradicts low risk climate.",
        })

    # ─────────────────────────────────────────────
    # Rule C-2: Stress vs Capital
    # ─────────────────────────────────────────────
    if (
        label("strategy_stress") == "HIGH"
        and label("capital_pressure") == "LOW"
    ):
        violations.append({
            "rule_id": "C-2",
            "panels": ["strategy_stress", "capital_pressure"],
            "description": "High strategy stress contradicts low capital pressure.",
        })

    # ─────────────────────────────────────────────
    # Rule C-3: Calm Paradox
    # ─────────────────────────────────────────────
    if (
        label("market_regime") == "CALM"
        and label("risk_climate") == "HIGH"
    ):
        violations.append({
            "rule_id": "C-3",
            "panels": ["market_regime", "risk_climate"],
            "description": "Calm market contradicts high risk climate.",
        })

    if violations:
        return {
            "status": "CONTRADICTORY",
            "violations": violations,
            "confidence_impact": float(len(violations)),
        }

    return {
        "status": "CONSISTENT",
        "violations": [],
        "confidence_impact": 0.0,
    }
