from typing import Dict, Mapping
from core.capital.attribution.attribution_record import CapitalAttributionRecord
from core.capital.allocation.allocator import StrategyCapitalSignal


class CapitalAttributionEngine:
    """
    Deterministic capital attribution engine.

    Converts allocation outputs into governance-grade explanations.
    """

    def explain(
        self,
        *,
        signals: Mapping[str, StrategyCapitalSignal],
        weights: Mapping[str, float],
    ) -> Dict[str, CapitalAttributionRecord]:

        records = {}

        for dna, signal in signals.items():
            raw_score = signal.ssr * signal.confidence * signal.regime_score

            records[dna] = CapitalAttributionRecord(
                dna=dna,
                final_weight=weights.get(dna, 0.0),
                ssr=signal.ssr,
                confidence=signal.confidence,
                regime_score=signal.regime_score,
                raw_score=raw_score,
            )

        return records
