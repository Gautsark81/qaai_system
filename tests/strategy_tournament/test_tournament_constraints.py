import pytest
from modules.strategy_tournament.dna import StrategyDNA
from modules.strategy_tournament.axes import *
from modules.strategy_tournament.constraints import validate_dna


def test_invalid_fade_high_efficiency():
    dna = StrategyDNA(
        MarketStructure.BALANCED,
        RegimeState.NORMAL_VOL,
        RegimeTransition.NONE,
        LiquidityModel.VWAP_REVERSION,
        EfficiencyState.HIGH,
        SessionState.MID,
        EntryType.FADE,
        RiskShape.FAST_STOP_FAST_TARGET,
        ExitIntent.VWAP_MEAN,
        PortfolioRole.DRAWDOWN_HEDGE,
    )

    with pytest.raises(ValueError):
        validate_dna(dna)
