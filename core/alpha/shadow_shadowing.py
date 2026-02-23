from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Iterable, List

from core.execution.execution_intent import ExecutionIntent
from core.alpha.shadow_diagnostics import ShadowAlphaDiagnostics, analyze_shadow_alpha


# ============================================================
# Shadow Strategy Result (Immutable, Observational)
# ============================================================

@dataclass(frozen=True)
class ShadowStrategyResult:
    """
    Result of a shadow strategy evaluation.

    HARD LAWS:
    - Must NOT affect execution
    - Must NOT affect capital
    - Must be deterministic
    """

    strategy_id: str
    hypothetical_intent: ExecutionIntent
    diagnostics: ShadowAlphaDiagnostics
    confidence_score: float


# ============================================================
# Shadow Strategy Runner (Pure, Parallel-Safe)
# ============================================================

def run_shadow_strategies(
    *,
    signal: Dict[str, Any],
    shadow_strategy_ids: Iterable[str],
) -> List[ShadowStrategyResult]:
    """
    Run multiple shadow strategies in parallel (conceptually).

    Produces hypothetical intents and diagnostics
    without affecting execution.
    """

    results: List[ShadowStrategyResult] = []

    for strategy_id in shadow_strategy_ids:
        # --------------------------------------------------
        # Hypothetical intent (deterministic variation)
        # --------------------------------------------------

        hypothetical_intent = ExecutionIntent(
            symbol=signal["symbol"],
            side=signal["side"],
            quantity=signal["quantity"],
            strategy_id=strategy_id,
            metadata={
                "shadow": True,
                "hypothetical": True,
            },
        )

        # --------------------------------------------------
        # Diagnostics (pure observation)
        # --------------------------------------------------

        diagnostics = analyze_shadow_alpha(
            signal=signal,
            intent=hypothetical_intent,
        )

        results.append(
            ShadowStrategyResult(
                strategy_id=strategy_id,
                hypothetical_intent=hypothetical_intent,
                diagnostics=diagnostics,
                confidence_score=diagnostics.confidence_score,
            )
        )

    return results
