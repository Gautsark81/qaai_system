from __future__ import annotations

from decimal import Decimal
from typing import Dict

from .promotion_intelligence import (
    PromotionIntelligenceEngine,
    PromotionIntelligenceArtifact,
)


# ---------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------


class PromotionIntelligenceReplayMismatch(Exception):
    """
    Raised when deterministic replay does not match expected state_hash.
    """

    pass


# ---------------------------------------------------------------------
# Replay Verifier
# ---------------------------------------------------------------------


class PromotionIntelligenceReplayVerifier:
    """
    C6.3 — Deterministic Promotion Intelligence Replay Verifier

    HARD GUARANTEES:
    - Pure deterministic replay
    - No authority
    - No lifecycle mutation
    - No capital mutation
    - No promotion execution
    """

    def __init__(
        self,
        *,
        engine: PromotionIntelligenceEngine | None = None,
    ):
        self.engine = engine or PromotionIntelligenceEngine()

    # -----------------------------------------------------------------

    def replay(
        self,
        *,
        strategy_dna: str,
        ssr_strength: Decimal,
        regime_alignment: Decimal,
        capital_fit: Decimal,
        governance_health: Decimal,
        weights: Dict[str, Decimal] | None = None,
    ) -> PromotionIntelligenceArtifact:
        """
        Deterministically recompute intelligence artifact.
        """

        return self.engine.score(
            strategy_dna=strategy_dna,
            ssr_strength=ssr_strength,
            regime_alignment=regime_alignment,
            capital_fit=capital_fit,
            governance_health=governance_health,
            weights=weights,
        )

    # -----------------------------------------------------------------

    def verify(
        self,
        *,
        expected_state_hash: str,
        **inputs,
    ) -> None:
        """
        Verify that replay reproduces stored state_hash.
        """

        artifact = self.replay(**inputs)

        if artifact.state_hash != expected_state_hash:
            raise PromotionIntelligenceReplayMismatch(
                f"Promotion intelligence hash mismatch: "
                f"expected={expected_state_hash}, "
                f"actual={artifact.state_hash}"
            )


# ---------------------------------------------------------------------
# Backward compatibility alias required by replay verifier tests
# ---------------------------------------------------------------------

PromotionIntelligence = PromotionIntelligenceEngine