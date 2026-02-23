from modules.strategy_selector.selector import (
    StrategySelector,
    SelectorConfig,
)
from modules.strategy_health.state_machine import StrategyState


def test_only_active_allowed_by_default():
    selector = StrategySelector(
        config=SelectorConfig()
    )

    strategies = {
        "NIFTY": ["s1", "s2", "s3"],
    }

    states = {
        "s1": StrategyState.ACTIVE,
        "s2": StrategyState.WARNING,
        "s3": StrategyState.PAUSED,
    }

    result = selector.select(
        strategies_by_symbol=strategies,
        states=states,
    )

    assert result.eligible["NIFTY"] == ["s1"]
    assert "s2" in result.blocked["NIFTY"]
    assert "s3" in result.blocked["NIFTY"]


def test_warning_allowed_when_configured():
    selector = StrategySelector(
        config=SelectorConfig(allow_warning=True)
    )

    strategies = {"BANKNIFTY": ["a", "b"]}
    states = {
        "a": StrategyState.WARNING,
        "b": StrategyState.ACTIVE,
    }

    result = selector.select(
        strategies_by_symbol=strategies,
        states=states,
    )

    assert set(result.eligible["BANKNIFTY"]) == {"a", "b"}


def test_degraded_not_allowed_by_default():
    selector = StrategySelector(
        config=SelectorConfig()
    )

    strategies = {"RELIANCE": ["x"]}
    states = {
        "x": StrategyState.DEGRADED,
    }

    result = selector.select(
        strategies_by_symbol=strategies,
        states=states,
    )

    assert result.eligible["RELIANCE"] == []
    assert "x" in result.blocked["RELIANCE"]


def test_allow_degraded_explicit():
    selector = StrategySelector(
        config=SelectorConfig(allow_degraded=True)
    )

    strategies = {"INFY": ["s1"]}
    states = {
        "s1": StrategyState.DEGRADED,
    }

    result = selector.select(
        strategies_by_symbol=strategies,
        states=states,
    )

    assert result.eligible["INFY"] == ["s1"]


def test_max_strategies_per_symbol_enforced():
    selector = StrategySelector(
        config=SelectorConfig(max_strategies_per_symbol=1)
    )

    strategies = {"TCS": ["a", "b"]}
    states = {
        "a": StrategyState.ACTIVE,
        "b": StrategyState.ACTIVE,
    }

    result = selector.select(
        strategies_by_symbol=strategies,
        states=states,
    )

    assert len(result.eligible["TCS"]) == 1
