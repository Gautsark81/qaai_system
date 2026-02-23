from itertools import product
from .axes import *
from .dna import StrategyDNA
from .constraints import validate_dna


class StrategyGenerator:
    def generate(self) -> list[StrategyDNA]:
        candidates = []

        for combo in product(
            MarketStructure,
            RegimeState,
            RegimeTransition,
            LiquidityModel,
            EfficiencyState,
            SessionState,
            EntryType,
            RiskShape,
            ExitIntent,
            PortfolioRole,
        ):
            dna = StrategyDNA(*combo)

            try:
                validate_dna(dna)
            except ValueError:
                continue

            candidates.append(dna)

        return candidates
