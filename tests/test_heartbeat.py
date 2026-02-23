# tests/test_heartbeat.py
from infra.heartbeat import Heartbeat
from providers.dhan_provider import DhanProvider


def test_heartbeat_reconnects():
    dp = DhanProvider(config={"starting_cash": 1000})
    # initially disconnected
    hb = Heartbeat(provider=dp, reconnect_attempts=2, reconnect_backoff=0.0)
    assert not dp.is_connected()
    ok = hb.check_and_reconnect()
    assert ok is True
    assert dp.is_connected()
