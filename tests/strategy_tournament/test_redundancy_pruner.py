from modules.strategy_tournament.redundancy_pruner import RedundancyPruner
from modules.strategy_tournament.result_schema import TradeResult
from modules.strategy_tournament.dna import StrategyDNA
from modules.strategy_tournament.axes import (
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
)


def _trade(symbol, et, xt, pnl):
    return TradeResult(
        symbol=symbol,
        entry_time=et,
        exit_time=xt,
        side="BUY",
        qty=1,
        entry_price=100,
        exit_price=100 + pnl,
        pnl=pnl,
        reason="test",
    )


def _dna(entry: EntryType) -> StrategyDNA:
    """
    Helper to build valid StrategyDNA using
    REAL enum values from axes.py
    """
    return StrategyDNA(
        MarketStructure.BALANCED,
        RegimeState.NORMAL_VOL,
        RegimeTransition.NONE,
        LiquidityModel.VWAP_REVERSION,
        EfficiencyState.LOW,          # ✅ FIXED (was MEDIUM)
        SessionState.MID,
        entry,
        RiskShape.FAST_STOP_FAST_TARGET,
        ExitIntent.VWAP_MEAN,
        PortfolioRole.RETURN_GENERATOR,
    )


def test_prunes_highly_correlated_strategy():
    pruner = RedundancyPruner(
        max_corr=0.8,
        max_overlap=0.8,
        min_dna_distance=0.2,
    )

    strategies = ["s1", "s2"]

    pnl_series = {
        "s1": [1, 2, 3, 4],
        "s2": [1, 2, 3, 4],
    }

    trades = {
        "s1": [_trade("A", "t1", "t2", 1)],
        "s2": [_trade("A", "t1", "t2", 1)],
    }

    dna_map = {
        "s1": _dna(EntryType.BREAKOUT),
        "s2": _dna(EntryType.BREAKOUT),
    }

    survivors = pruner.prune(
        strategies=strategies,
        pnl_series=pnl_series,
        trades=trades,
        dna_map=dna_map,
    )

    assert survivors == ["s1"]


def test_keeps_diverse_strategies():
    pruner = RedundancyPruner(
        max_corr=0.8,
        max_overlap=0.5,
        min_dna_distance=0.4,
    )

    strategies = ["s1", "s2"]

    pnl_series = {
        "s1": [1, -1, 1, -1],
        "s2": [-1, 1, -1, 1],
    }

    trades = {
        "s1": [_trade("A", "t1", "t2", 1)],
        "s2": [_trade("B", "t3", "t4", 1)],
    }

    dna_map = {
        "s1": _dna(EntryType.BREAKOUT),
        "s2": _dna(EntryType.FADE),
    }

    survivors = pruner.prune(
        strategies=strategies,
        pnl_series=pnl_series,
        trades=trades,
        dna_map=dna_map,
    )

    assert set(survivors) == {"s1", "s2"}
