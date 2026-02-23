from domain.canary.canary_mode import CanaryMode


def test_canary_modes_exist():
    assert CanaryMode.LIVE.value == "LIVE"
