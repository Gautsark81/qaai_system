# tests/unit/test_scheduler.py
import asyncio
import pytest
from infra.scheduler import AsyncScheduler

@pytest.mark.asyncio
async def test_scheduler_runs_job_and_stops(tmp_path):
    scheduler = AsyncScheduler()
    run_count = {"n": 0}
    async def job():
        run_count["n"] += 1
    # start job
    task = scheduler.start_job("tst", job, interval_s=0.01)
    await asyncio.sleep(0.05)
    assert run_count["n"] > 0
    await scheduler.stop_all()
    assert "tst" not in scheduler.list_jobs()
