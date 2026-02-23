# tests/strategies/test_ise_probability_strategy.py

from typing import Any, Dict, List

from screening.results import ScreeningResult

from strategies.ise_probability import (
    ISEProbabilityConfig,
    ISEProbabilityEngine,
    ISEProbabilityStrategy,
)


# ---------------------------
# Fake StrategyContext
# ---------------------------
class FakeContext:
    """
    Minimal StrategyContext for strategy tests.

    Provides:
      - watchlist(name)
      - get_feature_snapshot(symbol, timeframe)
      - get_l2_snapshot(symbol)
      - get_vwap(symbol, timeframe)
      - get_anchored_vwap(symbol, anchor_id)
    """

    def __init__(self, watchlists, features, l2, vwap, anchored_vwap):
        # watchlists: {name: [symbols]}
        # features: {(symbol, timeframe): dict}
        self._watchlists = dict(watchlists)
        self._features = dict(features)
        self._l2 = dict(l2)
        self._vwap = dict(vwap)
        self._anchored_vwap = dict(anchored_vwap)

    @property
    def universe_symbols(self):
        # Not needed by tests, but often part of StrategyContext
        return sorted({sym for syms in self._watchlists.values() for sym in syms})

    def watchlist(self, name: str):
        return list(self._watchlists.get(name, []))

    def get_feature_snapshot(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        return self._features.get((symbol, timeframe), {})

    def get_l2_snapshot(self, symbol: str) -> Dict[str, Any]:
        return self._l2.get(symbol, {})

    def get_vwap(self, symbol: str, timeframe: str) -> float:
        return self._vwap.get((symbol, timeframe))

    def get_anchored_vwap(self, symbol: str, anchor_id: str) -> float:
        return self._anchored_vwap.get((symbol, anchor_id))


# ---------------------------
# Tests
# ---------------------------
def test_ise_probability_strategy_emits_signals_for_high_prob_candidates():
    """
    High-probability candidate in watchlist should produce a StrategySignal
    with win_prob >= min_win_prob, while low-prob symbol is filtered out.
    """
    cfg = ISEProbabilityConfig(
        name="ISE_STRAT",
        timeframe="1m",
        higher_timeframes=("5m", "15m"),
        watchlist_name="DAY_SCALP",
        min_win_prob=0.75,
        max_positions=5,
        use_l2=True,
        use_ob_fvg=True,
        use_vwap_bias=True,
        use_mtfa_filter=True,
        use_ml_confidence=True,
        ml_enabled=False,
    )

    # NIFTY = high-quality setup
    # BANKNIFTY = low-quality setup
    features = {
        # main tf
        ("NIFTY", "1m"): {
            "close": 101.0,
            "last_price": 101.0,
            "liq_sweep": 1.0,
            "order_block": 1.0,
            "fvg": 1.0,
            "regime": "trend",
            "atr": 1.0,
            "sweep_anchor_id": "sw1",
        },
        # higher tfs aligned
        ("NIFTY", "5m"): {"trend_strength": 1.0},
        ("NIFTY", "15m"): {"trend_strength": 1.0},

        ("BANKNIFTY", "1m"): {
            "close": 100.0,
            "last_price": 100.0,
            "liq_sweep": 0.0,
            "order_block": 0.0,
            "fvg": 0.0,
            "regime": "chop",
            "atr": 1.5,
        },
        ("BANKNIFTY", "5m"): {"trend_strength": 0.0},
        ("BANKNIFTY", "15m"): {"trend_strength": 0.0},
    }

    l2 = {
        "NIFTY": {
            "bid_volume": 2000.0,
            "ask_volume": 1000.0,
            "buy_volume_delta": 500.0,
            "sell_volume_delta": 100.0,
        },
        "BANKNIFTY": {
            "bid_volume": 1000.0,
            "ask_volume": 1000.0,
            "buy_volume_delta": 0.0,
            "sell_volume_delta": 0.0,
        },
    }

    vwap = {
        ("NIFTY", "1m"): 100.0,       # NIFTY above VWAP => long bias OK
        ("BANKNIFTY", "1m"): 100.0,   # BANKNIFTY flat vs VWAP
    }

    anchored_vwap = {
        ("NIFTY", "sw1"): 99.5,
    }

    watchlists = {
        "DAY_SCALP": ["NIFTY", "BANKNIFTY"],
    }

    ctx = FakeContext(watchlists, features, l2, vwap, anchored_vwap)
    engine = ISEProbabilityEngine(cfg, ml_model=None)
    strat = ISEProbabilityStrategy(cfg, engine)

    screening_results = {
        "ISE_SCREEN": [
            ScreeningResult(symbol="NIFTY", score=1.0),
            ScreeningResult(symbol="BANKNIFTY", score=1.0),
        ]
    }

    signals = strat.generate_signals(ctx, screening_results)

    # Expect only NIFTY to pass all filters and probability threshold
    assert len(signals) == 1
    sig = signals[0]
    assert sig.symbol == "NIFTY"
    assert sig.side == "BUY"  # score positive
    assert sig.size > 0
    assert sig.meta["win_prob"] >= cfg.min_win_prob
    assert sig.meta["features"]["mtf_agree"] == 1.0
    assert sig.meta["features"]["liq_sweep"] == 1.0
    assert sig.meta["features"]["order_block"] == 1.0
    assert sig.meta["features"]["fvg"] == 1.0


def test_ise_probability_strategy_respects_vwap_bias_for_buy_side():
    """
    When VWAP bias is enabled:
      - A BUY signal should not be emitted if price is below VWAP (bias < 0).
    """
    cfg = ISEProbabilityConfig(
        name="ISE_STRAT",
        timeframe="1m",
        higher_timeframes=("5m", "15m"),
        watchlist_name="DAY_SCALP",
        min_win_prob=0.6,
        use_vwap_bias=True,
    )

    features = {
        ("NIFTY", "1m"): {
            "close": 99.0,          # price below VWAP
            "last_price": 99.0,
            "liq_sweep": 1.0,
            "order_block": 1.0,
            "fvg": 1.0,
            "regime": "trend",
            "atr": 1.0,
            "sweep_anchor_id": "sw1",
        },
        ("NIFTY", "5m"): {"trend_strength": 1.0},
        ("NIFTY", "15m"): {"trend_strength": 1.0},
    }

    l2 = {
        "NIFTY": {
            "bid_volume": 2000.0,
            "ask_volume": 1000.0,
        }
    }

    vwap = {("NIFTY", "1m"): 100.0}   # VWAP above price -> bias negative
    anchored_vwap = {("NIFTY", "sw1"): 100.0}

    watchlists = {"DAY_SCALP": ["NIFTY"]}
    ctx = FakeContext(watchlists, features, l2, vwap, anchored_vwap)
    engine = ISEProbabilityEngine(cfg, ml_model=None)
    strat = ISEProbabilityStrategy(cfg, engine)

    screening_results = {
        "ISE_SCREEN": [ScreeningResult(symbol="NIFTY", score=1.0)]
    }

    signals = strat.generate_signals(ctx, screening_results)
    # Even if handcrafted probability is high, BUY should be filtered by VWAP bias
    assert signals == []


def test_ise_probability_strategy_filters_by_watchlist_and_max_positions():
    """
    Strategy should only trade symbols in the configured watchlist and
    limit the number of positions to max_positions.
    """
    cfg = ISEProbabilityConfig(
        name="ISE_STRAT",
        timeframe="1m",
        higher_timeframes=("5m", "15m"),
        watchlist_name="DAY_SCALP",
        min_win_prob=0.6,
        max_positions=2,
    )

    # Three symbols with similar high-quality setups
    syms = ["A", "B", "C"]
    features = {}
    vwap = {}
    l2 = {}
    anchored_vwap = {}

    for s in syms:
        features[(s, "1m")] = {
            "close": 101.0,
            "last_price": 101.0,
            "liq_sweep": 1.0,
            "order_block": 1.0,
            "fvg": 1.0,
            "regime": "trend",
            "atr": 1.0,
        }
        features[(s, "5m")] = {"trend_strength": 1.0}
        features[(s, "15m")] = {"trend_strength": 1.0}
        vwap[(s, "1m")] = 100.0
        l2[s] = {"bid_volume": 2000.0, "ask_volume": 1000.0}

    watchlists = {
        "DAY_SCALP": ["A", "B", "C"],
        "OTHER": ["X", "Y"],
    }

    ctx = FakeContext(watchlists, features, l2, vwap, anchored_vwap)
    engine = ISEProbabilityEngine(cfg, ml_model=None)
    strat = ISEProbabilityStrategy(cfg, engine)

    screening_results = {
        "ISE_SCREEN": [
            ScreeningResult(symbol=s, score=1.0) for s in syms
        ]
    }

    signals = strat.generate_signals(ctx, screening_results)
    # Should trade only up to max_positions
    assert len(signals) == cfg.max_positions
    # All should be from the intended watchlist
    assert all(sig.symbol in watchlists["DAY_SCALP"] for sig in signals)
