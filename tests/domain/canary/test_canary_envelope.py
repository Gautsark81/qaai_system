from domain.canary.canary_envelope import CanaryEnvelope


def test_canary_envelope_caps():
    env = CanaryEnvelope(10, 4000)
    assert env.clamp(1000) == 1000
    assert env.clamp(5) is None
    assert env.clamp(5000) is None
