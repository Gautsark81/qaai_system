from typing import Dict, List
import numpy as np

from modules.strategy_tournament.overlap import trade_overlap_ratio
from modules.strategy_tournament.dna import StrategyDNA
from modules.strategy_tournament.dna_distance import dna_distance


class RedundancyPruner:
    """
    Removes redundant strategies while preserving diversification.

    FINAL INVARIANTS:
    - Negative or zero correlation is DIVERSIFYING → never pruned by DNA
    - DNA similarity only matters if behavior is already redundant
    - Correlation and overlap gate DNA pruning
    """

    def __init__(
        self,
        max_corr: float,
        max_overlap: float,
        min_dna_distance: float,
    ):
        self.max_corr = max_corr
        self.max_overlap = max_overlap
        self.min_dna_distance = min_dna_distance

    def _signed_correlation(self, a: List[float], b: List[float]) -> float:
        if len(a) < 2 or len(b) < 2:
            return 0.0
        try:
            return float(np.corrcoef(a, b)[0, 1])
        except Exception:
            return 0.0

    def prune(
        self,
        strategies: List[str],
        pnl_series: Dict[str, List[float]],
        trades: Dict[str, list],
        dna_map: Dict[str, StrategyDNA],
    ) -> List[str]:

        survivors: List[str] = []

        for sid in strategies:
            keep = True

            for kept in survivors:
                # -------------------------------------------------
                # Correlation (SIGNED)
                # -------------------------------------------------
                corr = self._signed_correlation(
                    pnl_series.get(sid, []),
                    pnl_series.get(kept, []),
                )

                # High POSITIVE correlation → redundancy
                if corr >= self.max_corr:
                    keep = False
                    break

                # -------------------------------------------------
                # Trade overlap
                # -------------------------------------------------
                overlap = trade_overlap_ratio(
                    trades.get(sid, []),
                    trades.get(kept, []),
                )

                if overlap >= self.max_overlap:
                    keep = False
                    break

                # -------------------------------------------------
                # DNA similarity (ONLY if behavior is redundant)
                # -------------------------------------------------
                if corr > 0 or overlap > 0:
                    dist = dna_distance(
                        dna_map[sid],
                        dna_map[kept],
                    )

                    if dist < self.min_dna_distance:
                        keep = False
                        break

            if keep:
                survivors.append(sid)

        return survivors
