from __future__ import annotations

from typing import Any, Dict

from .promotion_intelligence import PromotionIntelligence
from .promotion_intelligence_trace import PromotionIntelligenceTrace
from .promotion_intelligence_exceptions import (
    PromotionIntelligenceReplayMismatch,
)


class PromotionIntelligenceReplayVerifier:
    """
    C6.3 — Deterministic Promotion Intelligence Replay Verifier

    HARD GUARANTEES:
    - Pure deterministic reconstruction
    - No lifecycle mutation
    - No capital mutation
    - No execution authority
    - No registry mutation
    - Hash-stable replay
    """

    def __init__(
        self,
        *,
        intelligence: PromotionIntelligence,
    ):
        self.intelligence = intelligence

    # ------------------------------------------------------------------
    # Deterministic reconstruction
    # ------------------------------------------------------------------

    def replay(
        self,
        *,
        strategy_snapshot: Any,
        capital_snapshot: Any,
        screening_snapshot: Any,
        governance_snapshot: Any,
    ) -> PromotionIntelligenceTrace:
        """
        Rebuild Promotion Intelligence trace deterministically
        using the same inputs as original execution.
        """

        decision = self.intelligence.evaluate(
            strategy_snapshot=strategy_snapshot,
            capital_snapshot=capital_snapshot,
            screening_snapshot=screening_snapshot,
            governance_snapshot=governance_snapshot,
        )

        return decision.trace

    # ------------------------------------------------------------------
    # Hash verification
    # ------------------------------------------------------------------

    def verify(
        self,
        *,
        expected_trace_hash: str,
        **replay_inputs: Dict[str, Any],
    ) -> bool:
        """
        Verify deterministic replay reproduces stored trace hash.
        """

        trace = self.replay(**replay_inputs)

        if trace.trace_hash != expected_trace_hash:
            raise PromotionIntelligenceReplayMismatch(
                f"Promotion intelligence trace mismatch. "
                f"Expected={expected_trace_hash}, "
                f"Actual={trace.trace_hash}"
            )

        return True