# tests/strategies/test_ise_probability_engine.py

from typing import Any, Dict, List, Optional

from strategies.ise_probability import (
    ISEProbabilityConfig,
    ISEProbabilityEngine,
    ISEFeatureVector,
)


# ---------------------------
# Fake online ML model
# ---------------------------
class DummyOnlineProbModel:
    """
    Minimal implementation of OnlineProbModel:
      - predict_proba returns high win prob (0.8) for any input.
      - partial_fit just records calls.
    """

    def __init__(self) -> None:
        self.fitted_samples: int = 0
        self.last_X: Optional[List[List[float]]] = None
        self.last_y: Optional[List[int]] = None

    def predict_proba(self, X: List[List[float]]) -> List[List[float]]:
        # Always predict [p0, p1] = [0.2, 0.8]
        return [[0.2, 0.8] for _ in X]

    def partial_fit(
        self,
        X: List[List[float]],
        y: List[int],
        classes: List[int],
        sample_weight: Optional[List[float]] = None,
    ) -> None:
        self.fitted_samples += len(X)
        self.last_X = X
        self.last_y = y


# ---------------------------
# Fake StrategyContext for engine tests
# ---------------------------
class FakeContext:
    """
    Minimal context supplying:
      - get_feature_snapshot(symbol, timeframe)
      - get_l2_snapshot(symbol)
      - get_vwap(symbol, timeframe)
      - get_anchored_vwap(symbol, anchor_id)
    """

    def __init__(self, features, l2, vwap, anchored_vwap):
        # features: {(symbol, timeframe): dict}
        self._features = dict(features)
        self._l2 = dict(l2)
        self._vwap = dict(vwap)
        self._anchored_vwap = dict(anchored_vwap)

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
def test_ise_probability_engine_handcrafted_probability_boosts():
    """
    When all edge components (sweep, OB/FVG, VWAP bias, MTFA) are aligned,
    win probability should be well above the base 0.5.
    """
    cfg = ISEProbabilityConfig(
        name="ISE_TEST",
        use_l2=True,
        use_ob_fvg=True,
        use_vwap_bias=True,
        use_mtfa_filter=True,
        use_ml_confidence=True,  # ML model will be None => handcrafted
    )

    # Strong bullish context for NIFTY
    features = {
        # main timeframe (1m)
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
        # 5m + 15m trend alignment
        ("NIFTY", "5m"): {"trend_strength": 1.0},
        ("NIFTY", "15m"): {"trend_strength": 1.0},
    }

    l2 = {
        "NIFTY": {
            "bid_volume": 2000.0,
            "ask_volume": 1000.0,
            "buy_volume_delta": 500.0,
            "sell_volume_delta": 100.0,
        }
    }

    vwap = {
        ("NIFTY", "1m"): 100.0,  # price above vwap => bullish bias
    }

    anchored_vwap = {
        ("NIFTY", "sw1"): 99.5,  # price above anchored vwap
    }

    ctx = FakeContext(features, l2, vwap, anchored_vwap)
    engine = ISEProbabilityEngine(cfg, ml_model=None)

    fv = engine.build_features(ctx, "NIFTY")
    assert fv is not None

    p = engine.predict_win_prob(fv)
    # With all components aligned, handcrafted probability should be high
    assert p > 0.75
    assert p <= 0.95


def test_ise_probability_engine_low_signal_probability_near_base():
    """
    When almost no edges are present (no sweep, no OB/FVG, no MTFA, no bias),
    probability should stay close to the base (~0.5), not in 80%+ range.
    """
    cfg = ISEProbabilityConfig(
        name="ISE_TEST",
        use_l2=True,
        use_ob_fvg=True,
        use_vwap_bias=True,
        use_mtfa_filter=True,
        use_ml_confidence=True,
    )

    features = {
        ("NIFTY", "1m"): {
            "close": 100.0,
            "last_price": 100.0,
            "liq_sweep": 0.0,
            "order_block": 0.0,
            "fvg": 0.0,
            "regime": "chop",
            "atr": 1.5,
        },
        ("NIFTY", "5m"): {"trend_strength": 0.0},
        ("NIFTY", "15m"): {"trend_strength": 0.0},
    }

    l2 = {
        "NIFTY": {
            "bid_volume": 1000.0,
            "ask_volume": 1000.0,
            "buy_volume_delta": 0.0,
            "sell_volume_delta": 0.0,
        }
    }

    vwap = {("NIFTY", "1m"): 100.0}
    anchored_vwap = {}

    ctx = FakeContext(features, l2, vwap, anchored_vwap)
    engine = ISEProbabilityEngine(cfg, ml_model=None)

    fv = engine.build_features(ctx, "NIFTY")
    assert fv is not None

    p = engine.predict_win_prob(fv)
    assert 0.4 <= p <= 0.7


def test_ise_probability_engine_online_ml_overrides_handcrafted():
    """
    When ml_enabled and ml_model provided, and _seen_samples >= ml_min_conf_samples,
    engine should use predict_proba instead of handcrafted mapping.
    """
    cfg = ISEProbabilityConfig(
        name="ISE_TEST",
        use_l2=False,
        use_ob_fvg=False,
        use_vwap_bias=False,
        use_mtfa_filter=False,
        use_ml_confidence=True,
        ml_enabled=True,
        ml_min_conf_samples=1,  # small for test
    )

    dummy_model = DummyOnlineProbModel()
    engine = ISEProbabilityEngine(cfg, ml_model=dummy_model)

    # Simple feature vector
    fv = ISEFeatureVector(
        x=[0.0, 0.0, 0.0],
        meta={"regime": "trend", "atr": 1.0},
    )

    # First update with outcome => partial_fit called, _seen_samples increments
    engine.update_with_outcome(fv, outcome_win=True)
    assert dummy_model.fitted_samples == 1

    # Now predict -> should use dummy_model.predict_proba => ~0.8
    p = engine.predict_win_prob(fv)
    assert p > 0.75
    assert p <= 0.9
