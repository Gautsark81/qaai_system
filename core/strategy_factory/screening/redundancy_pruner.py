from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from .screening_models import ScreeningScore, ScreeningResult
from .screening_hash import compute_screening_state_hash


class RedundancyPruner:
    """
    C5.3 — Redundancy Pruner

    HARD RULES:
    - Deterministic
    - No lifecycle mutation
    - No capital mutation
    - No authority
    """

    # -------------------------------------------------------------
    # Primary public API (new style)
    # -------------------------------------------------------------
    def apply(
        self,
        base_result: ScreeningResult,
        redundancy_matrix: Optional[Dict[str, Dict[str, Decimal]]] = None,
        threshold: Optional[Decimal] = None,
    ) -> ScreeningResult:
        return self.prune(
            base_result=base_result,
            correlation_matrix=redundancy_matrix,
            threshold=threshold,
        )

    # -------------------------------------------------------------
    # Backward-compatible API
    # -------------------------------------------------------------
    def prune(
        self,
        base_result: ScreeningResult,
        correlation_matrix: Optional[Dict[str, Dict[str, Decimal]]] = None,
        threshold: Optional[Decimal] = None,
    ) -> ScreeningResult:
        """
        Supported modes:

        1) prune(result)  → no pruning
        2) prune(result, matrix, threshold)
        """

        # -----------------------------------------
        # Backward compatibility simple mode
        # -----------------------------------------
        if correlation_matrix is None or threshold is None:
            return base_result

        kept = []
        removed = set()

        # Deterministic iteration
        for s in base_result.scores:
            if s.strategy_dna in removed:
                continue

            kept.append(s)

            for other in base_result.scores:
                if other.strategy_dna == s.strategy_dna:
                    continue

                corr = (
                    correlation_matrix
                    .get(s.strategy_dna, {})
                    .get(other.strategy_dna, Decimal("0"))
                )

                if corr >= threshold:
                    removed.add(other.strategy_dna)

        # Re-rank deterministically
        kept = sorted(
            kept,
            key=lambda x: (-x.score, x.strategy_dna),
        )

        final_scores = []
        for idx, s in enumerate(kept, start=1):
            final_scores.append(
                ScreeningScore(
                    strategy_dna=s.strategy_dna,
                    score=s.score,
                    rank=idx,
                    metrics_hash=s.metrics_hash,
                )
            )

        return ScreeningResult(
            scores=tuple(final_scores),
            state_hash=compute_screening_state_hash(final_scores),
        )