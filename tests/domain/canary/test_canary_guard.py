from domain.canary.canary_guard import CanaryGuard
from domain.canary.canary_mode import CanaryMode
from domain.canary.canary_envelope import CanaryEnvelope


def test_canary_guard_allows_valid_trade():
    env = CanaryEnvelope(10, 4000)
    result = CanaryGuard.approve(CanaryMode.LIVE, env, 500)
    assert result == ("LIVE_EXECUTION", 500)


def test_canary_guard_blocks_invalid_trade():
    env = CanaryEnvelope(10, 4000)
    assert CanaryGuard.approve(CanaryMode.LIVE, env, 9000) is None
