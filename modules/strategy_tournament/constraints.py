from .dna import StrategyDNA
from .axes import *


def validate_dna(dna: StrategyDNA) -> None:
    if dna.role == PortfolioRole.DRAWDOWN_HEDGE and dna.entry == EntryType.BREAKOUT:
        raise ValueError("Drawdown hedge cannot be breakout-driven")

    if dna.transition != RegimeTransition.NONE:
        if dna.structure in {MarketStructure.BALANCED, MarketStructure.EXHAUSTING}:
            return
        raise ValueError("Invalid regime transition for structure")

    if dna.entry == EntryType.FADE and dna.efficiency == EfficiencyState.HIGH:
        raise ValueError("Fade cannot operate under high efficiency")

    if dna.risk == RiskShape.TRAILING_ONLY and dna.role == PortfolioRole.TAIL_RISK_CAPTURE:
        raise ValueError("Tail capture requires asymmetric targets")
