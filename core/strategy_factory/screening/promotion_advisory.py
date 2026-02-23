from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .screening_models import ScreeningResult


@dataclass(frozen=True)
class PromotionAdvisory:
    """
    C5.11 — Promotion Advisory Adapter

    PURE INTELLIGENCE SURFACE.

    HARD GUARANTEES:
    - No lifecycle mutation
    - No capital mutation
    - No registry access
    - No promotion triggering
    - Deterministic
    - Replay-stable
    - Fully advisory
    """

    ranked_strategies: Tuple[str, ...]
    recommended_for_paper: Tuple[str, ...]
    recommended_for_live: Tuple[str, ...]
    base_state_hash: str


class PromotionAdvisoryAdapter:
    """
    Deterministic advisory builder from ScreeningResult.
    """

    def __init__(
        self,
        *,
        top_n_for_paper: int = 3,
        live_rank_threshold: int = 1,
    ):
        self._top_n_for_paper = top_n_for_paper
        self._live_rank_threshold = live_rank_threshold

    # ------------------------------------------------------------------
    # Pure advisory construction
    # ------------------------------------------------------------------

    def build(
        self,
        *,
        screening_result: ScreeningResult,
    ) -> PromotionAdvisory:
        """
        Build deterministic advisory from screening result.

        Policy (stable, deterministic):
        - ranked_strategies: order from ScreeningResult
        - recommended_for_paper: top N ranked strategies
        - recommended_for_live: strategies whose rank <= live_rank_threshold
        """

        scores = screening_result.scores

        ranked = tuple(s.strategy_dna for s in scores)

        recommended_for_paper = tuple(
            s.strategy_dna
            for s in scores[: self._top_n_for_paper]
        )

        recommended_for_live = tuple(
            s.strategy_dna
            for s in scores
            if s.rank <= self._live_rank_threshold
        )

        return PromotionAdvisory(
            ranked_strategies=ranked,
            recommended_for_paper=recommended_for_paper,
            recommended_for_live=recommended_for_live,
            base_state_hash=screening_result.state_hash,
        )