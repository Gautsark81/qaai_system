from typing import Dict, Mapping, Optional

from core.capital.capital_contracts import StrategyCapitalSignal


class PortfolioCapitalAllocator:
    """
    Institutional portfolio-level capital allocator.

    Guarantees:
    - Hard min_weight enforcement
    - No execution side effects
    - No exceptions
    - Deterministic

    NOTE:
    This allocator is authoritative.
    Any evidence emission is strictly observational.
    """

    def allocate(
        self,
        *,
        signals: Mapping[str, StrategyCapitalSignal],
        min_weight: float = 0.0,
        evidence_store: Optional[object] = None,  # optional, read-only
    ) -> Dict[str, float]:

        # ============================
        # Step 1: raw scores
        # ============================
        raw_scores: Dict[str, float] = {
            dna: max(0.0, s.ssr * s.confidence * s.regime_score)
            for dna, s in signals.items()
        }

        if not raw_scores:
            return {}

        # ============================
        # Step 2: separate floored vs free
        # ============================
        floored = {
            dna for dna, score in raw_scores.items()
            if score > 0.0 and min_weight > 0.0
        }

        free = set(raw_scores.keys()) - floored

        # ============================
        # Step 3: reserve floor capital
        # ============================
        floor_capital = min_weight * len(floored)

        if floor_capital >= 1.0:
            weights = {
                dna: (1.0 / len(floored)) if dna in floored else 0.0
                for dna in raw_scores
            }
        else:
            remaining_capital = 1.0 - floor_capital

            # ============================
            # Step 4: distribute remaining capital
            # ============================
            free_scores_sum = sum(raw_scores[dna] for dna in free)

            weights: Dict[str, float] = {}

            for dna in raw_scores:
                if dna in floored:
                    weights[dna] = min_weight
                elif free_scores_sum > 0.0:
                    weights[dna] = (
                        raw_scores[dna] / free_scores_sum
                    ) * remaining_capital
                else:
                    weights[dna] = 0.0

            # ============================
            # Step 5: final sanity normalization
            # ============================
            total = sum(weights.values())
            if total > 0.0:
                weights = {dna: w / total for dna, w in weights.items()}

        # ============================
        # Step 6: READ-ONLY evidence emission (optional)
        # ============================
        if evidence_store is not None:
            try:
                from core.capital.evidence_emitter import (
                    emit_capital_allocation_evidence,
                )

                emit_capital_allocation_evidence(
                    signals=dict(signals),
                    allocations=weights,
                    capital_available=1.0,  # portfolio-normalized
                    store=evidence_store,
                )
            except Exception:
                # Evidence must NEVER affect allocation
                pass

        return weights
