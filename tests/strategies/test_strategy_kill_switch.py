# tests/strategies/test_strategy_kill_switch.py

import pytest
from modules.strategies.base import BaseStrategy
from modules.strategies.health.types import StrategyState


class ExplodingStrategy(BaseStrategy):
    def _run(self, *_):
        raise RuntimeError("boom")


def make_strategy():
    return ExplodingStrategy(
        strategy_id="bad_strategy",
        version="1.0",
        symbol="NIFTY",
        timeframe="5m",
        params={},
    )


def test_strategy_disabled_after_repeated_failures():
    s = make_strategy()

    for _ in range(3):
        with pytest.raises(RuntimeError):
            s.run({})

    # fourth run must be blocked
    assert s.run({}) is None


def test_disabled_strategy_emits_no_intent():
    s = make_strategy()

    for _ in range(3):
        try:
            s.run({})
        except RuntimeError:
            pass

    assert s.run({}) is None
