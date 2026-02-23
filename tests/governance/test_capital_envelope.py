from modules.governance.capital_envelope import (
    CapitalEnvelope,
    CapitalEnvelopeValidator,
)


def test_capital_within_limits():
    env = CapitalEnvelope(max_capital=1_000_000, max_daily_loss=20_000)
    assert CapitalEnvelopeValidator().validate(500_000, env)


def test_capital_exceeds_limits():
    env = CapitalEnvelope(max_capital=1_000_000, max_daily_loss=20_000)
    assert not CapitalEnvelopeValidator().validate(2_000_000, env)
