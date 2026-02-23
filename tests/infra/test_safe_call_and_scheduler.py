# tests/infra/test_safe_call_and_scheduler.py
import asyncio

import pytest

from infra.safe_call import safe_call_async, safe_call_sync
from infra.scheduler import AsyncScheduler


@pytest.mark.asyncio
async def test_safe_call_async_retries_and_success():
    state = {"calls": 0}

    async def flaky():
        state["calls"] += 1
        if state["calls"] < 2:
            raise RuntimeError("boom")
        return "ok"

    result = await safe_call_async(flaky, retries=3, backoff_base=0.01)
    assert result == "ok"
    assert state["calls"] == 2


def test_safe_call_sync_retries_and_success():
    state = {"calls": 0}

    def flaky():
        state["calls"] += 1
        if state["calls"] < 2:
            raise RuntimeError("boom")
        return "ok"

    result = safe_call_sync(flaky, retries=3, backoff_base=0.0)
    assert result == "ok"
    assert state["calls"] == 2


@pytest.mark.asyncio
async def test_async_scheduler_runs_jobs():
    scheduler = AsyncScheduler()
    state = {"runs": 0}

    async def job():
        state["runs"] += 1

    # start a job that runs every 0.05s and also runs once immediately
    scheduler.start_job(
        "test_job",
        job,
        interval_s=0.05,
        run_immediately=True,
    )

    await asyncio.sleep(0.12)
    await scheduler.stop_all()

    # We should have run at least twice (immediate + one/two loops)
    assert state["runs"] >= 2
    assert scheduler.list_jobs() == []
