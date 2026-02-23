from enum import Enum
from core.strategy_factory.health.death_reason import DeathReason

def test_death_reason_enum_values():
    assert DeathReason.MAX_DRAWDOWN.value == "max_drawdown"
    assert DeathReason.SSR_FAILURE.value == "ssr_failure"
    assert DeathReason.CONSECUTIVE_LOSSES.value == "consecutive_losses"
    assert DeathReason.VOLATILITY_REGIME.value == "volatility_regime"
    assert DeathReason.MARKET_STRUCTURE.value == "market_structure"
    assert DeathReason.OPERATOR_KILL.value == "operator_kill"
    assert DeathReason.SYSTEM_GUARDRAIL.value == "system_guardrail"


def test_death_reason_is_enum():
    assert issubclass(DeathReason, Enum)


def test_death_reason_string_conversion():
    reason = DeathReason.MAX_DRAWDOWN
    assert str(reason) == "max_drawdown"


def test_death_reason_from_string():
    assert DeathReason.from_str("max_drawdown") == DeathReason.MAX_DRAWDOWN
    assert DeathReason.from_str("ssr_failure") == DeathReason.SSR_FAILURE
