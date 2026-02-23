"""
Root-level daily scheduler for qaai_system.

This is a cron-style, time-of-day scheduler built on top of the
`schedule` library, running in a background thread.

Use this for:
- Pre-market screening at 09:00 IST
- Intraday watchlist refresh at specific clock times
- Forced exit / liquidation routines at 15:15 IST

For high-frequency / interval-based jobs, use infra.AsyncScheduler instead.
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, time as dtime
from typing import Callable, Optional

import schedule  # type: ignore[import]

from infra.logging import get_logger
from infra.time_utils import IST, now_ist

logger = get_logger("scheduler.cron")


# ----------------------------------------------------------------------
# Internal state
# ----------------------------------------------------------------------
_scheduler_thread: Optional[threading.Thread] = None
_stop_flag = threading.Event()


def _run_loop(poll_interval_seconds: float = 30.0) -> None:
    logger.info(
        "cron_scheduler_thread_started",
        extra={
            "poll_interval_seconds": poll_interval_seconds,
            "started_at_ist": now_ist().isoformat(),
        },
    )
    while not _stop_flag.is_set():
        try:
            schedule.run_pending()
        except Exception as exc:
            logger.error(
                "cron_scheduler_run_pending_error", extra={"error": str(exc)}
            )
        time.sleep(poll_interval_seconds)

    logger.info(
        "cron_scheduler_thread_stopped",
        extra={"stopped_at_ist": now_ist().isoformat()},
    )


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def start_scheduler_in_background(poll_interval_seconds: float = 30.0) -> None:
    """
    Start the schedule.run_pending loop in a background daemon thread.

    Should be called once when your application starts (e.g. in the
    main orchestrator).
    """
    global _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        logger.info("cron_scheduler_already_running")
        return

    _stop_flag.clear()
    _scheduler_thread = threading.Thread(
        target=_run_loop, args=(poll_interval_seconds,), daemon=True
    )
    _scheduler_thread.start()


def stop_scheduler() -> None:
    """
    Signal the scheduler thread to stop and wait for it.
    """
    global _scheduler_thread
    if not _scheduler_thread:
        return

    logger.info("cron_scheduler_stop_request")
    _stop_flag.set()
    _scheduler_thread.join(timeout=5.0)
    _scheduler_thread = None
    logger.info("cron_scheduler_stop_done")


def clear_all_jobs() -> None:
    """
    Remove all scheduled jobs from the `schedule` registry.
    """
    schedule.clear()
    logger.info("cron_scheduler_jobs_cleared")


# ----------------------------------------------------------------------
# Helper registration functions: "Hybrid" patterns
# ----------------------------------------------------------------------
def schedule_daily_job_at(
    at_time_ist: str,
    job_fn: Callable[[], None],
    job_name: Optional[str] = None,
) -> None:
    """
    Schedule a job to run every day at a specific IST clock time.

    at_time_ist: "HH:MM" format in IST, e.g. "09:00", "15:15".
    job_fn: synchronous function with no arguments.
    job_name: optional label for logging.
    """
    job_label = job_name or job_fn.__name__
    schedule.every().day.at(at_time_ist).do(job_fn)
    logger.info(
        "cron_scheduler_job_registered",
        extra={"job": job_label, "at_time_ist": at_time_ist},
    )


def schedule_watchlist_update(
    job_fn: Callable[[], None], at_time_ist: str = "09:00"
) -> None:
    """
    Convenience wrapper for pre-market / scheduled watchlist updates.
    """
    schedule_daily_job_at(at_time_ist, job_fn, job_name="watchlist_update")


def schedule_intraday_liquidation(
    job_fn: Callable[[], None], at_time_ist: str = "15:15"
) -> None:
    """
    Convenience wrapper for forced liquidation / exit-all jobs.
    """
    schedule_daily_job_at(at_time_ist, job_fn, job_name="intraday_liquidation")


def schedule_custom_window_job(
    start_time_ist: dtime,
    end_time_ist: dtime,
    job_fn: Callable[[], None],
    *,
    interval_minutes: int = 5,
    job_name: Optional[str] = None,
) -> None:
    """
    "Hybrid" pattern: periodically run a job between [start_time, end_time] IST.

    This is useful for:
    - Running a lighter screener during the session
    - Periodic monitoring jobs within the trading window

    NOTE: This uses schedule.every(interval).minutes.do(job_fn).
    The job_fn itself should check the current IST time and
    no-op if outside the window, e.g.:

        def my_job():
            now = now_ist().time()
            if not (start <= now <= end):
                return
            ...

    That makes the schedule definition simple and keeps control in your code.
    """
    job_label = job_name or job_fn.__name__
    schedule.every(interval_minutes).minutes.do(job_fn)
    logger.info(
        "cron_scheduler_window_job_registered",
        extra={
            "job": job_label,
            "interval_minutes": interval_minutes,
            "start_ist": start_time_ist.isoformat(),
            "end_ist": end_time_ist.isoformat(),
        },
    )
