# infra/healthcheck.py
from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from .exceptions import HealthcheckError
from .logging import get_logger
from .time_utils import now_ist

logger = get_logger(__name__)


@dataclass
class HealthStatus:
    component: str
    ok: bool
    message: str
    details: Dict[str, Any]
    ts_ist: str

    @classmethod
    def ok_status(cls, component: str, message: str = "OK", **details: Any) -> "HealthStatus":
        return cls(
            component=component,
            ok=True,
            message=message,
            details=details,
            ts_ist=now_ist().isoformat(),
        )

    @classmethod
    def fail_status(cls, component: str, message: str, **details: Any) -> "HealthStatus":
        return cls(
            component=component,
            ok=False,
            message=message,
            details=details,
            ts_ist=now_ist().isoformat(),
        )


async def check_redis(redis_client: Any) -> HealthStatus:
    try:
        pong = await redis_client.ping()
        if pong is True or pong == "PONG":
            return HealthStatus.ok_status("redis", ping=pong)
        return HealthStatus.fail_status("redis", "Unexpected PING response", ping=pong)
    except Exception as exc:
        return HealthStatus.fail_status("redis", f"Redis ping failed: {exc!s}")


async def check_dhan(dhan_client: Any) -> HealthStatus:
    """
    Expects dhan_client to expose an async `healthcheck()` or `get_profile()` / `get_funds()`.

    You can easily adapt your existing DhanSafeClient by adding a small `async def healthcheck`.
    """
    try:
        if hasattr(dhan_client, "healthcheck"):
            await dhan_client.healthcheck()
        elif hasattr(dhan_client, "get_profile"):
            await dhan_client.get_profile()
        elif hasattr(dhan_client, "get_funds"):
            await dhan_client.get_funds()
        else:
            return HealthStatus.fail_status(
                "dhan",
                "No suitable healthcheck method on dhan_client",
            )
        return HealthStatus.ok_status("dhan")
    except Exception as exc:
        return HealthStatus.fail_status("dhan", f"Dhan check failed: {exc!s}")


async def check_clock_drift(max_drift_seconds: float = 5.0) -> HealthStatus:
    """
    Simple local monotonic vs wall-clock sanity check.
    NOTE: for full NTP-based drift checks, integrate an external time source later.
    """
    t0 = time.time()
    wall = now_ist().timestamp()
    t1 = time.time()

    # These should be close; any huge discrepancy is suspicious.
    drift = abs((t0 + t1) / 2.0 - wall)
    if drift <= max_drift_seconds:
        return HealthStatus.ok_status("clock", drift_seconds=drift)
    return HealthStatus.fail_status("clock", "Clock drift too large", drift_seconds=drift)


async def run_all_healthchecks(
    *,
    redis_client: Optional[Any] = None,
    dhan_client: Optional[Any] = None,
) -> List[HealthStatus]:
    checks: List[HealthStatus] = []

    if redis_client is not None:
        checks.append(await check_redis(redis_client))

    if dhan_client is not None:
        checks.append(await check_dhan(dhan_client))

    checks.append(await check_clock_drift())

    # Log a single summary line
    summary = {
        "components": {c.component: c.ok for c in checks},
    }
    logger.info("healthcheck_summary", extra={"summary": summary})

    # If any critical component failed, raise
    if any(not c.ok for c in checks):
        raise HealthcheckError(f"Healthcheck failed: {summary!r}")

    return checks
