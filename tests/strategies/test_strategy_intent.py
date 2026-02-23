# tests/strategies/test_strategy_intent.py

import pytest
from datetime import datetime

from modules.strategies.factory import StrategyFactory
from modules.strategies.spec import StrategySpec
from modules.strategies.intent import StrategyIntent
from modules.strategies.intent_validator import validate_intent
from modules.strategies.base import BaseStrategy


def test_strategy_emits_intent():
    spec = StrategySpec(
        strategy_id="s1",
        strategy_type="ema_cross",
        version="1.0",
        symbol="NIFTY",
        timeframe="5m",
        params={},
    )

    strategy = StrategyFactory.create(spec)

    intent = strategy.run({"ema_fast": 12, "ema_slow": 10})

    assert intent is None or isinstance(intent, StrategyIntent)

class BadStrategy(BaseStrategy):
    def _run(self, *_):
        return {"side": "BUY"}  # ❌ illegal output


def test_invalid_strategy_output_rejected():
    """
    Any non-StrategyIntent output must fail hard.
    """
    s = BadStrategy(
        strategy_id="x",
        version="1.0",
        symbol="NIFTY",
        timeframe="5m",
        params={},
    )

    with pytest.raises(TypeError):
        s.run({})


def test_confidence_bounds_enforced():
    """
    Confidence must be within [0.0, 1.0].
    """
    intent = StrategyIntent(
        strategy_id="s",
        symbol="NIFTY",
        side="BUY",
        confidence=1.5,  # ❌ invalid
        features_used=[],
        timestamp=datetime.utcnow(),
    )

    with pytest.raises(ValueError):
        validate_intent(intent)
