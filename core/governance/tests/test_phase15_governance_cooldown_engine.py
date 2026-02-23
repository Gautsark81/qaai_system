from core.governance.escalation.cooldown_engine import (
    GovernanceCooldownEngine,
    CooldownPolicy,
)


def test_throttle_decay_after_required_windows():
    engine = GovernanceCooldownEngine(
        policy=CooldownPolicy(clean_windows_required=3)
    )

    result = engine.evaluate(
        governance_id="gov-1",
        current_strikes=2,
        escalation_level="THROTTLE",
        clean_windows=3,
    )

    assert result.strike_reduced is True
    assert result.new_strike_count == 1


def test_freeze_requires_double_windows():
    engine = GovernanceCooldownEngine(
        policy=CooldownPolicy(clean_windows_required=3, freeze_multiplier=2)
    )

    # Only 3 windows — insufficient for FREEZE
    result = engine.evaluate(
        governance_id="gov-2",
        current_strikes=2,
        escalation_level="FREEZE",
        clean_windows=3,
    )

    assert result.strike_reduced is False
    assert result.new_strike_count == 2

    # 6 windows — sufficient
    result2 = engine.evaluate(
        governance_id="gov-2",
        current_strikes=2,
        escalation_level="FREEZE",
        clean_windows=6,
    )

    assert result2.strike_reduced is True
    assert result2.new_strike_count == 1


def test_zero_capital_never_auto_decays():
    engine = GovernanceCooldownEngine()

    result = engine.evaluate(
        governance_id="gov-3",
        current_strikes=3,
        escalation_level="ZERO_CAPITAL",
        clean_windows=100,
    )

    assert result.strike_reduced is False
    assert result.new_strike_count == 3


def test_no_strikes_no_action():
    engine = GovernanceCooldownEngine()

    result = engine.evaluate(
        governance_id="gov-4",
        current_strikes=0,
        escalation_level="NONE",
        clean_windows=10,
    )

    assert result.strike_reduced is False
    assert result.new_strike_count == 0