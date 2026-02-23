from core.strategy_factory.registry import StrategyRegistry
from core.phase_b.advisory import AdvisorySignal


class ConfidenceEngine:
    """
    Phase B intelligence engine (READ-ONLY).
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def compute(self, dna: str) -> AdvisorySignal:
        record = self.registry.get(dna)

        # Placeholder logic (replace later with ML / SSR)
        confidence = 1.0 if record.state in ("PAPER", "LIVE") else 0.5

        return AdvisorySignal(
            dna=dna,
            confidence=confidence,
            note="advisory_only",
        )
