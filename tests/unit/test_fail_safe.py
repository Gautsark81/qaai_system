# tests/unit/test_fail_safe.py
import pytest
import asyncio
from infra.fail_safe import retry, CircuitBreaker

def test_retry_sync():
    calls = {"n": 0}
    @retry(max_attempts=3, base_delay=0.01, jitter=0.0, exceptions=(ValueError,))
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("fail")
        return "ok"
    assert flaky() == "ok"
    assert calls["n"] == 2

@pytest.mark.asyncio
async def test_retry_async():
    calls = {"n": 0}
    @retry(max_attempts=3, base_delay=0.01, jitter=0.0, exceptions=(ValueError,))
    async def flaky_async():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("fail")
        return "ok"
    res = await flaky_async()
    assert res == "ok"
    assert calls["n"] == 2

def test_circuit_breaker_trips():
    cb = CircuitBreaker(fail_max=2, reset_timeout=0.1)
    def failer():
        raise RuntimeError("boom")
    with pytest.raises(RuntimeError):
        cb.call(failer)
    with pytest.raises(RuntimeError):
        cb.call(failer)
    # next call should open circuit
    with pytest.raises(RuntimeError):
        cb.call(failer)
    # now circuit is open -> calling should raise circuit open before underlying call
    with pytest.raises(RuntimeError):
        cb.call(lambda: 1)
