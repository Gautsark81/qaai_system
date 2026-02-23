from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple

from .screening_models import ScreeningScore, ScreeningResult


@dataclass(frozen=True)
class ScreeningGovernanceSnapshot:
    """
    C5.9 — Screening Governance Snapshot

    HARD GUARANTEES:
    - Immutable
    - Deterministic
    - No lifecycle mutation
    - No capital mutation
    - No registry mutation
    - Advisory only
    """

    ranked_strategies: Tuple[str, ...]
    state_hash: str
    advisory_strength: Decimal
    regime: str | None


class ScreeningGovernanceBridge:
    """
    Converts ScreeningResult into a governance-safe immutable snapshot.
    """

    def build(
        self,
        *,
        screening_result: ScreeningResult,
        regime: str | None = None,
    ) -> ScreeningGovernanceSnapshot:

        # Deterministic extraction (already sorted by rank)
        ranked = tuple(s.strategy_dna for s in screening_result.scores)

        # Advisory strength = normalized top score signal
        if not screening_result.scores:
            strength = Decimal("0")
        else:
            top_score = screening_result.scores[0].score
            strength = Decimal(top_score)

        return ScreeningGovernanceSnapshot(
            ranked_strategies=ranked,
            state_hash=screening_result.state_hash,
            advisory_strength=strength,
            regime=regime,
        )