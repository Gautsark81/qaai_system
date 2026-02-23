# tests/infra/test_healthcheck_stubs.py
import asyncio

import pytest

from infra.healthcheck import (
    HealthStatus,
    check_clock_drift,
    check_redis,
    check_dhan,
    run_all_healthchecks,
)
from infra.exceptions import HealthcheckError


class FakeRedis:
    async def ping(self):
        return "PONG"


class FakeDhan:
    async def healthcheck(self):
        return True


@pytest.mark.asyncio
async def test_healthstatus_helpers():
    ok = HealthStatus.ok_status("x", foo="bar")
    fail = HealthStatus.fail_status("y", "nope", code=1)

    assert ok.ok is True and ok.component == "x" and ok.details["foo"] == "bar"
    assert fail.ok is False and fail.component == "y" and fail.details["code"] == 1


@pytest.mark.asyncio
async def test_health_checks_individual():
    redis_status = await check_redis(FakeRedis())
    assert redis_status.ok

    dhan_status = await check_dhan(FakeDhan())
    assert dhan_status.ok

    clock_status = await check_clock_drift(max_drift_seconds=60.0)
    assert clock_status.ok


@pytest.mark.asyncio
async def test_run_all_healthchecks_ok():
    statuses = await run_all_healthchecks(
        redis_client=FakeRedis(), dhan_client=FakeDhan()
    )
    assert all(s.ok for s in statuses)


@pytest.mark.asyncio
async def test_run_all_healthchecks_failure_raises():
    class BadRedis(FakeRedis):
        async def ping(self):
            raise RuntimeError("boom")

    with pytest.raises(HealthcheckError):
        await run_all_healthchecks(redis_client=BadRedis())
