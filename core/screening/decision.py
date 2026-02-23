from typing import Dict, List, Tuple, Any
from core.screening.models import ScreeningDecision


def make_decision(
    *,
    score: float,
    rules: Dict[str, Dict[str, Any]] | None = None,
    symbol: str | None = None,
    reasons: List[str] | None = None,
) -> Tuple[bool, List[str]] | ScreeningDecision:
    """
    Canonical decision wrapper.

    Supports TWO required modes (DO NOT REMOVE):

    1) TEST / RULE MODE
       make_decision(score=..., rules=...)
       -> returns (passed, reasons)

    2) OBJECT MODE (engine / pipeline)
       make_decision(score=..., symbol=..., reasons=...)
       -> returns ScreeningDecision
    """

    # -------------------------------------------------
    # MODE 1: Rule-based decision (used by tests)
    # -------------------------------------------------
    if rules is not None:
        failed = [name for name, r in rules.items() if not r.get("passed", False)]

        passed = len(failed) == 0

        # IMPORTANT: tests expect ALL rule names when passed
        decision_reasons = list(rules.keys()) if passed else failed

        return passed, decision_reasons

    # -------------------------------------------------
    # MODE 2: Object construction (production path)
    # -------------------------------------------------
    if symbol is None:
        raise ValueError("symbol is required when rules are not provided")

    final_reasons = reasons or (["passed"] if score > 0 else ["blocked"])

    return ScreeningDecision(
        symbol=symbol,
        passed=score > 0,
        reasons=final_reasons,
        score=score,
    )
