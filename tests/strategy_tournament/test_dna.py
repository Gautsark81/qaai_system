from modules.strategy_tournament.dna import StrategyDNA
from modules.strategy_tournament.axes import *


def test_dna_fingerprint_deterministic():
    dna1 = StrategyDNA(
        MarketStructure.BALANCED,
        RegimeState.NORMAL_VOL,
        RegimeTransition.NONE,
        LiquidityModel.VWAP_REVERSION,
        EfficiencyState.LOW,
        SessionState.MID,
        EntryType.FADE,
        RiskShape.FAST_STOP_FAST_TARGET,
        ExitIntent.VWAP_MEAN,
        PortfolioRole.DRAWDOWN_HEDGE,
    )
    dna2 = dna1
    assert dna1.fingerprint() == dna2.fingerprint()
