# infra/scheduler.py
"""
AsyncScheduler: hybrid, dynamic async job scheduler for qaai_system.

- Runs coroutine jobs at fixed intervals (seconds)
- Supports run_immediately, pause/resume, update interval
- Structured JSON logging via infra.logging
- Uses SchedulerError from infra.exceptions
- IST timestamps via infra.time_utils.now_ist

This is the core Phase-0 infra scheduler for:
- Health checks
- Intraday monitors
- Periodic maintenance tasks
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, Optional, Set

from infra.logging import get_logger
from infra.exceptions import SchedulerError
from infra.time_utils import now_ist

logger = get_logger("infra.scheduler")

CoroutineFunc = Callable[[], Awaitable[object]]


@dataclass
class JobState:
    name: str
    interval_s: float
    func: CoroutineFunc
    run_immediately: bool = False
    tags: Set[str] = field(default_factory=set)
    last_run_ist: Optional[str] = None
    next_run_ist: Optional[str] = None
    error_count: int = 0
    paused: bool = False


class AsyncScheduler:
    """
    Hybrid, dynamic async scheduler.

    Basic usage (what your tests already do):

        scheduler = AsyncScheduler()

        async def job():
            ...

        scheduler.start_job("my_job", job, interval_s=1.0, run_immediately=True)
        await asyncio.sleep(3)
        await scheduler.stop_all()

    Extra capabilities (supercharged):

        - pause_job("name") / resume_job("name")
        - update_interval("name", new_interval_s)
        - job_info("name") -> JobState snapshot
    """

    def __init__(self) -> None:
        # Map job name -> asyncio.Task
        self._tasks: Dict[str, asyncio.Task[object]] = {}
        # Map job name -> JobState
        self._jobs: Dict[str, JobState] = {}
        self._running: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start_job(
        self,
        name: str,
        coro_fn: CoroutineFunc,
        interval_s: float = 1.0,
        *,
        run_immediately: bool = False,
        tags: Optional[Set[str]] = None,
    ) -> asyncio.Task[object]:
        """
        Start a recurring async job.

        Parameters
        ----------
        name : str
            Unique job name.
        coro_fn : CoroutineFunc
            Coroutine function with no arguments.
        interval_s : float
            Interval in seconds between runs.
        run_immediately : bool
            Run once before the first sleep cycle.
        tags : Optional[Set[str]]
            Arbitrary tags, e.g. {"health", "risk"}.

        Raises
        ------
        SchedulerError
            If job name already exists.
        """
        if name in self._tasks:
            raise SchedulerError(f"Job {name!r} is already running")

        if interval_s <= 0:
            raise SchedulerError("interval_s must be positive")

        state = JobState(
            name=name,
            interval_s=interval_s,
            func=coro_fn,
            run_immediately=run_immediately,
            tags=tags or set(),
        )
        self._jobs[name] = state
        self._running = True

        task: asyncio.Task[object] = asyncio.create_task(
            self._runner(state),
            name=f"scheduler:{name}",
        )
        self._tasks[name] = task

        logger.info(
            "scheduler_job_registered",
            extra={
                "job": name,
                "interval_s": interval_s,
                "run_immediately": run_immediately,
                "tags": sorted(state.tags),
                "registered_at_ist": now_ist().isoformat(),
            },
        )
        return task

    async def stop_job(self, name: str, timeout: float = 5.0) -> None:
        """
        Cancel and await a specific job, then remove it.
        """
        task = self._tasks.get(name)
        if not task:
            logger.debug("scheduler_stop_job_missing", extra={"job": name})
            self._jobs.pop(name, None)
            return

        logger.info("scheduler_stop_job_request", extra={"job": name})
        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=timeout)
        except asyncio.CancelledError:
            logger.debug(
                "scheduler_stop_job_cancelled_while_waiting", extra={"job": name}
            )
        except asyncio.TimeoutError:
            logger.warning(
                "scheduler_stop_job_timeout",
                extra={"job": name, "timeout": timeout},
            )
        except Exception as exc:
            logger.exception(
                "scheduler_stop_job_unexpected_error",
                extra={"job": name, "error": str(exc)},
            )
        finally:
            self._tasks.pop(name, None)
            self._jobs.pop(name, None)

    async def stop_all(self, timeout: float = 5.0) -> None:
        """
        Cancel and await all jobs, then mark the scheduler as not running.
        """
        logger.info(
            "scheduler_stop_all_request", extra={"jobs": list(self._tasks.keys())}
        )
        names = list(self._tasks.keys())
        for name in names:
            await self.stop_job(name, timeout=timeout)
        self._running = False
        logger.info("scheduler_stop_all_done")

    def list_jobs(self) -> list[str]:
        """
        Return a list of currently registered job names.
        """
        return list(self._tasks.keys())

    def is_running(self) -> bool:
        """
        True if there is at least one active job.
        """
        return self._running and bool(self._tasks)

    # ------------------------------------------------------------------
    # Supercharged dynamic controls
    # ------------------------------------------------------------------
    def pause_job(self, name: str) -> None:
        state = self._jobs.get(name)
        if not state:
            raise SchedulerError(f"Job {name!r} not found")
        state.paused = True
        logger.info("scheduler_job_paused", extra={"job": name})

    def resume_job(self, name: str) -> None:
        state = self._jobs.get(name)
        if not state:
            raise SchedulerError(f"Job {name!r} not found")
        state.paused = False
        logger.info("scheduler_job_resumed", extra={"job": name})

    def update_interval(self, name: str, interval_s: float) -> None:
        if interval_s <= 0:
            raise SchedulerError("interval_s must be positive")
        state = self._jobs.get(name)
        if not state:
            raise SchedulerError(f"Job {name!r} not found")
        state.interval_s = interval_s
        logger.info(
            "scheduler_job_interval_updated",
            extra={"job": name, "interval_s": interval_s},
        )

    def job_info(self, name: str) -> Optional[JobState]:
        """
        Return a copy-like snapshot of job state (or None).
        Note: JobState is mutable; do not mutate in-place from callers.
        """
        return self._jobs.get(name)

    # ------------------------------------------------------------------
    # Internal runner
    # ------------------------------------------------------------------
    async def _runner(self, state: JobState) -> None:
        name = state.name
        logger.info(
            "scheduler_job_started",
            extra={
                "job": name,
                "interval_s": state.interval_s,
                "run_immediately": state.run_immediately,
                "tags": sorted(state.tags),
                "started_at_ist": now_ist().isoformat(),
            },
        )
        try:
            if state.run_immediately:
                await self._run_once(state)

            while self._running and name in self._jobs:
                # sleep first to avoid tight loops if interval gets very small
                try:
                    await asyncio.sleep(state.interval_s)
                except asyncio.CancelledError:
                    logger.debug(
                        "scheduler_job_cancelled_during_sleep", extra={"job": name}
                    )
                    raise

                await self._run_once(state)
        except asyncio.CancelledError:
            logger.info(
                "scheduler_job_cancel_request",
                extra={"job": name},
            )
        finally:
            logger.info(
                "scheduler_job_stopped",
                extra={"job": name, "stopped_at_ist": now_ist().isoformat()},
            )

    async def _run_once(self, state: JobState) -> None:
        name = state.name
        if state.paused:
            logger.debug("scheduler_job_paused_skip_run", extra={"job": name})
            return

        logger.debug(
            "scheduler_job_run_start",
            extra={"job": name, "interval_s": state.interval_s},
        )
        try:
            state.last_run_ist = now_ist().isoformat()
            await state.func()
            state.error_count = 0
        except asyncio.CancelledError:
            logger.debug(
                "scheduler_job_cancelled_during_execution", extra={"job": name}
            )
            raise
        except Exception as exc:
            state.error_count += 1
            logger.error(
                "scheduler_job_error",
                extra={"job": name, "error": str(exc), "error_count": state.error_count},
            )
