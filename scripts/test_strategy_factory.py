from core.strategy_factory.strategy_generator import StrategyGenerator
from core.strategy_factory.symbol_context_contract import SymbolContext


def test_strategy_factory_generation():
    symbol_contexts = {
        "NIFTY": {
            "price_above_vwap": True,
            "vwap_slope_positive": True,
            "volume_spike": True,
            "trend_strength": 0.8,
            "higher_high": True,
            "higher_low": True,
            "atr_pct": 0.012,
            "volatility_regime": "medium",
        }
    }

    strategies = StrategyGenerator().generate(symbol_contexts)

    assert strategies is not None
